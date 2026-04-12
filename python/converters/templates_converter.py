import json
import re
from pathlib import Path
from typing import Dict
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class TemplatesConverter:
    """Convert Django templates to Jinja2 (Flask) templates"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.rules = self._load_rules()
        self.results = {
            'converted_files': [],
            'total_templates': 0,
            'issues': [],
            'warnings': []
        }

    def _load_rules(self) -> Dict:
        """Load conversion rules from JSON"""
        rules_path = Path(__file__).parent.parent / 'rules' / 'templates_rules.json'
        with open(rules_path, 'r') as f:
            return json.load(f)

    def convert(self) -> Dict:
        """Convert all Django templates to Jinja2"""
        logger.info("Starting templates conversion")

        # Find all HTML templates
        template_files = FileHandler.find_files(str(self.django_path), '*.html')

        for template_file in template_files:
            try:
                result = self._convert_file(template_file)
                self.results['converted_files'].append(result)
                self.results['total_templates'] += 1

                # Add per-file conversion detail for frontend display
                self.results['issues'].append({
                    'file': str(template_file.relative_to(self.django_path)),
                    'filename': template_file.name,
                    'status': 'converted',
                    'confidence': 80,  # Moderate confidence - templates may need manual review
                    'message': 'Template converted to Jinja2',
                    'description': 'Django template tags converted to Jinja2 syntax',
                    'category': 'templates'
                })
            except Exception as e:
                logger.error(f"Failed to convert {template_file}: {e}")
                self.results['issues'].append({
                    'file': str(template_file.relative_to(self.django_path)),
                    'filename': template_file.name,
                    'status': 'failed',
                    'confidence': 0,
                    'message': f'Conversion failed: {str(e)}',
                    'description': str(e),
                    'category': 'templates',
                    'error': str(e)
                })

        logger.info(f"Templates conversion complete. Converted {self.results['total_templates']} templates")
        return self.results

    def _convert_file(self, file_path: Path) -> Dict:
        """Convert a single Django template file"""
        logger.debug(f"Converting template: {file_path}")

        source_code = FileHandler.read_file(str(file_path))
        converted_code = self._convert_template_code(source_code)

        # Calculate output path - preserve directory structure
        # Templates go into templates/ directory, maintaining app structure
        relative_path = file_path.relative_to(self.django_path)

        # Try to preserve the app/templates structure if it exists
        parts = relative_path.parts
        if 'templates' in parts:
            # Find templates directory and keep everything after it
            templates_idx = parts.index('templates')
            output_file = self.output_path / Path(*parts[templates_idx:])
        else:
            # No templates directory in path, just put in templates/
            output_file = self.output_path / 'templates' / relative_path.name

        # Write converted code
        FileHandler.write_file(str(output_file), converted_code)

        return {
            'file': str(file_path),
            'output': str(output_file),
            'success': True
        }

    def _convert_template_code(self, code: str) -> str:
        """Convert Django template syntax to Jinja2"""

        converted = code

        # --- Load tags ---
        # Remove {% load static %} (already handled)
        converted = re.sub(r'{%\s*load\s+static\s*%}\s*', '', converted)
        # Remove ALL remaining {% load ... %} tags (custom tag libraries not available in Jinja2)
        converted = re.sub(r'{%\s*load\s+\w+\s*%}\s*\n?', '', converted)

        # --- Static files ---
        # Convert {% static 'path' %} and {% static "path" %}
        converted = re.sub(
            r"""{%\s*static\s+['"]([^'"]+)['"]\s*%}""",
            r"{{ url_for('static', filename='\1') }}",
            converted
        )

        # --- URL tags ---
        # Convert {% url 'view_name' arg1 arg2 %} with positional and keyword args
        def replace_url_tag(match):
            view_name = match.group(1)
            args_str = (match.group(2) or '').strip()
            if not args_str:
                return f"{{{{ url_for('{view_name}') }}}}"

            named_args = re.findall(r'(\w+)=([^\s]+)', args_str)
            if named_args:
                kwargs = ', '.join(f"{key}={value}" for key, value in named_args)
                return f"{{{{ url_for('{view_name}', {kwargs}) }}}}"

            self.results['warnings'].append({
                'type': 'url_tag_arguments',
                'message': f'Positional arguments in url tag for "{view_name}" need manual verification'
            })
            return f"{{{{ url_for('{view_name}') }}}}"

        url_pattern = re.compile(r"""{%\s*url\s+['"]([^'"]+)['"]\s*([^%]*)%}""")
        converted = url_pattern.sub(replace_url_tag, converted)

        # --- CSRF ---
        converted = converted.replace('{% csrf_token %}', '{{ csrf_token() }}')

        # --- For-loop helpers ---
        converted = converted.replace('forloop.counter0', 'loop.index0')
        converted = converted.replace('forloop.counter', 'loop.index')
        converted = converted.replace('forloop.first', 'loop.first')
        converted = converted.replace('forloop.last', 'loop.last')
        converted = converted.replace('forloop.revcounter', 'loop.revindex')
        converted = converted.replace('forloop.revcounter0', 'loop.revindex0')
        converted = converted.replace('forloop.parentloop', 'loop')  # approximate
        converted = converted.replace('{% empty %}', '{% else %}')

        # --- with / endwith → set ---
        # {% with var=expr %} → {% set var = expr %}
        converted = re.sub(
            r'{%\s*with\s+(\w+)\s*=\s*(.+?)\s*%}',
            r'{% set \1 = \2 %}',
            converted
        )
        converted = re.sub(r'{%\s*endwith\s*%}', '', converted)

        # --- ifequal / endifequal → if x == y ---
        converted = re.sub(
            r'{%\s*ifequal\s+(\S+)\s+(\S+)\s*%}',
            r'{% if \1 == \2 %}',
            converted
        )
        converted = re.sub(r'{%\s*endifequal\s*%}', '{% endif %}', converted)

        # --- ifnotequal / endifnotequal → if x != y ---
        converted = re.sub(
            r'{%\s*ifnotequal\s+(\S+)\s+(\S+)\s*%}',
            r'{% if \1 != \2 %}',
            converted
        )
        converted = re.sub(r'{%\s*endifnotequal\s*%}', '{% endif %}', converted)

        # --- comment / endcomment → Jinja2 comment ---
        converted = re.sub(
            r'{%\s*comment\s*%}(.*?){%\s*endcomment\s*%}',
            r'{# \1 #}',
            converted, flags=re.DOTALL
        )

        # --- spaceless → whitespace control (remove the tags) ---
        converted = re.sub(r'{%\s*spaceless\s*%}', '', converted)
        converted = re.sub(r'{%\s*endspaceless\s*%}', '', converted)

        # --- now "format" → datetime formatting ---
        def replace_now_tag(match):
            django_fmt = match.group(1)
            py_fmt = self._convert_date_format(django_fmt)
            return f"{{{{ now().strftime('{py_fmt}') }}}}"
        converted = re.sub(r"""{%\s*now\s+['"]([^'"]+)['"]\s*%}""", replace_now_tag, converted)

        # --- Django template filters → Jinja2 ---

        # |date:"format" → .strftime('format') with format conversion
        def replace_date_filter(match):
            django_fmt = match.group(1)
            py_fmt = self._convert_date_format(django_fmt)
            return f"|strftime('{py_fmt}')"
        converted = re.sub(r"""\|date:['"]([^'"]+)['"]""", replace_date_filter, converted)

        # |default:"value" → |default("value")
        converted = re.sub(r"""\|default:['"]([^'"]*?)['"]""", r'|default("\1")', converted)
        converted = re.sub(r"""\|default:(\w+)""", r'|default(\1)', converted)

        # |add:"N" → + N  (numeric) or ~ "str" (string concat)
        def replace_add_filter(match):
            value = match.group(1)
            try:
                int(value)
                return f" + {value}"
            except ValueError:
                return f' ~ "{value}"'
        converted = re.sub(r"""\|add:['"]?([^'"}\s]+)['"]?""", replace_add_filter, converted)

        # |truncatewords:N → |truncate(N * 7, True)  (approx — 7 chars per word)
        converted = re.sub(
            r'\|truncatewords:(\d+)',
            lambda m: f"|truncate({int(m.group(1)) * 7}, True)",
            converted
        )

        # |linebreaks → |replace("\\n", "<br>")  (simplified)
        converted = converted.replace('|linebreaks', '|replace("\\n", "<br>")|safe')
        converted = converted.replace('|linebreaksbr', '|replace("\\n", "<br>")|safe')

        # |yesno:"yes,no,maybe" → ternary
        def replace_yesno(match):
            parts = match.group(1).split(',')
            yes_val = parts[0] if len(parts) > 0 else 'yes'
            no_val = parts[1] if len(parts) > 1 else 'no'
            return f'|yesno("{yes_val}", "{no_val}")'
        converted = re.sub(r"""\|yesno:['"]([^'"]+)['"]""", replace_yesno, converted)

        # |escape → |e
        converted = re.sub(r'\|escape\b', '|e', converted)

        # |floatformat → |round (approximate)
        converted = re.sub(r'\|floatformat:?(\d+)?', lambda m: f"|round({m.group(1) or 2})", converted)

        # |slugify → |replace(" ", "-")|lower (approximate)
        converted = converted.replace('|slugify', '|replace(" ", "-")|lower')

        # |capfirst → |capitalize
        converted = converted.replace('|capfirst', '|capitalize')

        # |pluralize → custom (leave but note)
        # |title → |title (compatible)
        # |upper → |upper (compatible)
        # |lower → |lower (compatible)
        # |length → |length (compatible)
        # |safe → |safe (compatible)
        # |join:"," → |join(",") (compatible)
        converted = re.sub(r"""\|join:['"]([^'"]+)['"]""", r'|join("\1")', converted)

        # |first → |first (compatible)
        # |last → |last (compatible)
        # |striptags → |striptags (compatible)

        # --- Form rendering shortcuts ---
        # {{ form.as_p }} → manual rendering note
        for form_method in ['as_p', 'as_table', 'as_ul']:
            converted = re.sub(
                rf'{{{{\s*(\w+)\.{form_method}\s*}}}}',
                r'{# TODO: Replace {{ \1.' + form_method + r' }} with explicit Jinja2 form rendering #}',
                converted
            )

        # Add comment at top
        if converted and not converted.startswith('<!--'):
            converted = '<!-- Converted from Django template to Jinja2 (Flask) -->\n' + converted

        return converted

    def _convert_date_format(self, django_format: str) -> str:
        """Convert Django date format string to Python strftime format."""
        # Django → Python strftime mapping
        format_map = {
            'Y': '%Y',  # 4-digit year
            'y': '%y',  # 2-digit year
            'm': '%m',  # Month as zero-padded decimal
            'n': '%-m', # Month without leading zero
            'd': '%d',  # Day as zero-padded decimal
            'j': '%-d', # Day without leading zero
            'H': '%H',  # Hour (24-hour) zero-padded
            'G': '%-H', # Hour (24-hour) without leading zero
            'h': '%I',  # Hour (12-hour) zero-padded
            'g': '%-I', # Hour (12-hour) without leading zero
            'i': '%M',  # Minutes zero-padded
            's': '%S',  # Seconds zero-padded
            'A': '%p',  # AM/PM
            'F': '%B',  # Full month name
            'M': '%b',  # Abbreviated month name
            'N': '%b',  # Abbreviated month (AP style, close to %b)
            'l': '%A',  # Full weekday name
            'D': '%a',  # Abbreviated weekday name
        }
        result = ''
        i = 0
        while i < len(django_format):
            char = django_format[i]
            if char in format_map:
                result += format_map[char]
            elif char == '\\' and i + 1 < len(django_format):
                # Escaped character — keep literal
                i += 1
                result += django_format[i]
            else:
                result += char
            i += 1
        return result


__all__ = ['TemplatesConverter']
