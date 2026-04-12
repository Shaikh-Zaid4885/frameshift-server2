"""
Advanced Templates Conversion Accuracy Improver
Handles complex Django templates → Jinja2 templates conversion with high accuracy
"""

import re
from typing import Dict, List, Optional, Tuple


class TemplatesAccuracyImprover:
    """
    Improves accuracy of Django templates → Jinja2 templates conversion
    Handles: template tags, filters, inheritance, loops, conditions, macros
    """

    def __init__(self):
        self.tag_mappings = self._build_tag_mappings()
        self.filter_mappings = self._build_filter_mappings()
        self.builtin_filters = self._build_builtin_filters()

    def _build_tag_mappings(self) -> Dict[str, str]:
        """Map Django template tags to Jinja2"""
        return {
            '{% if %}': '{% if %}',
            '{% for %}': '{% for %}',
            '{% block %}': '{% block %}',
            '{% extends %}': '{% extends %}',
            '{% include %}': '{% include %}',
            '{% load %}': '# Load static in Jinja2: {% set static = true %}',
            '{% static %}': '{{ url_for("static", filename="...") }}',
            '{% url %}': '{{ url_for("view_name", param=value) }}',
            '{% csrf_token %}': '{{ csrf_token() }}',
            '{% trans %}': '{{ _("text") }}',
            '{% comment %}': '{# comment #}',
            '{% verbatim %}': '{% raw %}',
        }

    def _build_filter_mappings(self) -> Dict[str, str]:
        """Map Django filters to Jinja2 filters"""
        return {
            'safe': 'safe',
            'escape': 'e',
            'length': 'length',
            'upper': 'upper',
            'lower': 'lower',
            'first': 'first',
            'last': 'last',
            'join': 'join',
            'slice': 'slice',
            'default': 'default',
            'date': 'strftime',
            'time': 'strftime',
            'floatformat': 'round',
            'add': 'add (custom)',
            'capfirst': 'title',
            'center': 'center (custom)',
            'cut': 'replace',
            'dictsort': 'dictsort',
            'divisibleby': 'divisibleby (custom)',
            'filesizeformat': 'filesizeformat (custom)',
            'linebreaks': 'replace',
            'linebreaksbr': 'replace',
            'linenumbers': 'enumerate (custom)',
            'pluralize': 'pluralize (custom)',
            'random': 'random',
            'slugify': 'slugify',
            'stringformat': 'format',
            'striptags': 'striptags (custom)',
            'truncatewords': 'truncate',
            'truncatewords_html': 'truncate (with html)',
            'urlize': 'urlize (custom)',
            'wordcount': 'wordcount (custom)',
            'wordwrap': 'wordwrap (custom)',
            'yesno': 'yesno (custom)',
        }

    def _build_builtin_filters(self) -> Dict[str, str]:
        """Jinja2 builtin filters mapping"""
        return {
            'safe': 'safe',
            'escape': 'e',
            'length': 'length',
            'upper': 'upper',
            'lower': 'lower',
            'title': 'title',
            'capitalize': 'capitalize',
            'reverse': 'reverse',
            'sort': 'sort',
            'unique': 'unique',
            'sum': 'sum',
            'min': 'min',
            'max': 'max',
            'abs': 'abs',
            'round': 'round',
            'int': 'int',
            'float': 'float',
            'string': 'string',
            'list': 'list',
            'dict': 'dict',
            'join': 'join',
            'split': 'split',
            'batch': 'batch',
            'slice': 'slice',
            'first': 'first',
            'last': 'last',
            'select': 'select',
            'reject': 'reject',
            'selectattr': 'selectattr',
            'rejectattr': 'rejectattr',
            'map': 'map',
            'groupby': 'groupby',
            'sum': 'sum',
            'indent': 'indent',
            'replace': 'replace',
            'format': 'format',
            'trim': 'trim',
            'striptags': 'striptags',
            'urlencode': 'urlencode',
            'urlize': 'urlize',
            'wordwrap': 'wordwrap',
            'wordcount': 'wordcount',
            'truncate': 'truncate',
            'default': 'default',
            'filesizeformat': 'filesizeformat',
            'pprint': 'pprint',
            'dictsort': 'dictsort',
            'tojson': 'tojson',
        }

    def improve_template_tags(self, template_code: str) -> str:
        """
        Improve Django template tags conversion
        """
        improved = template_code
        
        # Convert if/elif/else tags (already compatible)
        # But ensure spacing
        improved = re.sub(r"{%\s*if\s+", "{% if ", improved)
        improved = re.sub(r"{%\s*elif\s+", "{% elif ", improved)
        improved = re.sub(r"{%\s*else\s*%}", "{% else %}", improved)
        
        # Convert for loops
        improved = re.sub(
            r"{%\s*for\s+(\w+)\s+in\s+([^%}]+)\s*%}",
            r"{% for \1 in \2 %}",
            improved
        )
        
        improved = re.sub(
            r"{%\s*endfor\s*%}",
            "{% endfor %}",
            improved
        )
        
        improved = re.sub(
            r"{%\s*endif\s*%}",
            "{% endif %}",
            improved
        )
        
        # Convert empty/forloop checks
        improved = re.sub(
            r"forloop\.counter",
            "loop.index",
            improved
        )
        
        improved = re.sub(
            r"forloop\.counter0",
            "loop.index0",
            improved
        )
        
        improved = re.sub(
            r"forloop\.first",
            "loop.first",
            improved
        )
        
        improved = re.sub(
            r"forloop\.last",
            "loop.last",
            improved
        )
        
        # Convert empty check
        improved = re.sub(
            r"{%\s*empty\s*%}",
            "{% else %}",  # Jinja2 doesn't have empty, use else
            improved
        )
        
        return improved

    def improve_block_tags(self, template_code: str) -> str:
        """
        Improve block tag conversion
        """
        improved = template_code
        
        # Convert block tags (already compatible)
        improved = re.sub(
            r"{%\s*block\s+(\w+)\s*%}",
            r"{% block \1 %}",
            improved
        )
        
        improved = re.sub(
            r"{%\s*endblock\s+\w+?\s*%}",
            "{% endblock %}",
            improved
        )
        
        improved = re.sub(
            r"{%\s*endblock\s*%}",
            "{% endblock %}",
            improved
        )
        
        # Convert extends
        improved = re.sub(
            r"{%\s*extends\s+['\"]([^'\"]+)['\"]",
            r"{% extends '\1'",
            improved
        )
        
        # Convert include
        improved = re.sub(
            r"{%\s*include\s+['\"]([^'\"]+)['\"]",
            r"{% include '\1'",
            improved
        )
        
        return improved

    def improve_template_filters(self, template_code: str) -> str:
        """
        Convert Django template filters to Jinja2 filters
        """
        improved = template_code
        
        # Convert common filters
        filter_conversions = [
            (r"\|\s*safe\s*", "|safe"),
            (r"\|\s*escape\s*", "|e"),
            (r"\|\s*length\s*", "|length"),
            (r"\|\s*upper\s*", "|upper"),
            (r"\|\s*lower\s*", "|lower"),
            (r"\|\s*capitalize\s*", "|capitalize"),
            (r"\|\s*first\s*", "|first"),
            (r"\|\s*last\s*", "|last"),
            (r"\|\s*default:\s*(['\"][^'\"]*['\"])", r"|default(\1)"),
            (r"\|\s*join:\s*(['\"][^'\"]*['\"])", r"|join(\1)"),
        ]
        
        for pattern, replacement in filter_conversions:
            improved = re.sub(pattern, replacement, improved)
        
        # Convert date filter
        improved = re.sub(
            r"\|\s*date:\s*['\"]([^'\"]+)['\"]",
            lambda m: f"|strftime('{self._convert_date_format(m.group(1))}'))",
            improved
        )
        
        # Convert pluralize filter
        improved = re.sub(
            r"\|\s*pluralize(?::([^}]*))?\s*",
            "|pluralize",
            improved
        )
        
        # Convert add filter
        improved = re.sub(
            r"\|\s*add:\s*(\w+)",
            r" + \1",
            improved
        )
        
        # Convert truncatewords filter
        improved = re.sub(
            r"\|\s*truncatewords:\s*(\d+)",
            r"|truncate(length=\1*5, killwords=True)",
            improved
        )
        
        return improved

    def _convert_date_format(self, django_format: str) -> str:
        """Convert Django date format to Python strftime format"""
        conversions = {
            'Y': '%Y',  # 4-digit year
            'y': '%y',  # 2-digit year
            'm': '%m',  # Month
            'd': '%d',  # Day
            'H': '%H',  # Hour 24
            'h': '%I',  # Hour 12
            'i': '%M',  # Minute
            's': '%S',  # Second
            'A': '%p',  # AM/PM
            'b': '%b',  # Month abbrev
            'B': '%B',  # Month full
            'a': '%a',  # Day abbrev
            'E': '%A',  # Day full
        }
        
        result = django_format
        for django_char, strftime_char in conversions.items():
            result = result.replace(django_char, strftime_char)
        
        return result

    def improve_static_files(self, template_code: str) -> str:
        """
        Convert Django static file references to Flask
        """
        improved = template_code
        
        # Convert {% static %} tags
        improved = re.sub(
            r"{%\s*static\s+['\"]([^'\"]+)['\"].*?%}",
            r"{{ url_for('static', filename='\1') }}",
            improved
        )
        
        # Convert hardcoded /static/ paths
        improved = re.sub(
            r'href=["\']?/static/([^"\'>\s]+)',
            r'href="{{ url_for(\'static\', filename=\'\1\') }}"',
            improved
        )
        
        improved = re.sub(
            r'src=["\']?/static/([^"\'>\s]+)',
            r'src="{{ url_for(\'static\', filename=\'\1\') }}"',
            improved
        )
        
        return improved

    def improve_form_rendering(self, template_code: str) -> str:
        """
        Improve form rendering conversion
        """
        improved = template_code
        
        # Convert form rendering
        improved = re.sub(
            r"{{\s*form\.as_p\s*}}",
            "{{ form | as_p }}",
            improved
        )
        
        improved = re.sub(
            r"{{\s*form\.as_table\s*}}",
            "{{ form | as_table }}",
            improved
        )
        
        improved = re.sub(
            r"{{\s*form\.as_ul\s*}}",
            "{{ form | as_ul }}",
            improved
        )
        
        # Convert form field rendering
        improved = re.sub(
            r"{{\s*form\.(\w+)\s*}}",
            r"{{ form.\1 }}",
            improved
        )
        
        # Convert CSRF token
        improved = re.sub(
            r"{%\s*csrf_token\s*%}",
            "{{ csrf_token() }}",
            improved
        )
        
        return improved

    def improve_url_references(self, template_code: str) -> str:
        """
        Convert Django URL tags to Flask url_for
        """
        improved = template_code
        
        # Convert {% url %} tags with parameters
        improved = re.sub(
            r"{%\s*url\s+['\"](\w+)['\"](?:\s+([^%}]*?))?\s*%}",
            lambda m: self._convert_url_tag(m.group(1), m.group(2)),
            improved
        )
        
        # Convert href="{% url ... %}"
        improved = re.sub(
            r'href=["\']?{%\s*url\s+["\'](\w+)["\'](?:\s+([^%}]*?))?\s*%}["\']?',
            lambda m: f'href="{{{{ url_for(\'{m.group(1)}\'{self._extract_params(m.group(2))}) }}}}"',
            improved
        )
        
        return improved

    def _convert_url_tag(self, view_name: str, params: Optional[str]) -> str:
        """Convert individual {% url %} tag"""
        if params:
            # Extract key=value pairs
            param_pairs = re.findall(r'(\w+)=([^\s]+)', params or "")
            param_str = ", ".join([f"{k}={v}" for k, v in param_pairs])
            return f"{{{{ url_for('{view_name}', {param_str}) }}}}"
        else:
            return f"{{{{ url_for('{view_name}') }}}}"

    def _extract_params(self, params: Optional[str]) -> str:
        """Extract parameters from Django URL tag"""
        if not params:
            return ""
        
        param_pairs = re.findall(r'(\w+)=([^\s]+)', params)
        if param_pairs:
            param_str = ", ".join([f"{k}={v}" for k, v in param_pairs])
            return f", {param_str}"
        return ""

    def improve_template_variables(self, template_code: str) -> str:
        """
        Improve template variable handling
        """
        improved = template_code
        
        # Fix variable access spacing
        improved = re.sub(
            r"{{\s*(\w+(?:\.\w+)*)\s*}}",
            r"{{ \1 }}",
            improved
        )
        
        # Convert safe filter usage
        improved = re.sub(
            r"{{.*?\|\s*safe\s*}}",
            lambda m: m.group(0).replace("| safe", "|safe"),
            improved
        )
        
        return improved

    def improve_conditional_expressions(self, template_code: str) -> str:
        """
        Improve conditional expression handling
        """
        improved = template_code
        
        # Convert ternary-like expressions in templates
        # Django: {% if cond %}yes{% else %}no{% endif %}
        # Already compatible with Jinja2
        
        # Fix logical operators
        improved = re.sub(
            r"\band\b",
            "and",
            improved
        )
        
        improved = re.sub(
            r"\bor\b",
            "or",
            improved
        )
        
        improved = re.sub(
            r"\bnot\b",
            "not",
            improved
        )
        
        return improved

    def add_template_macros(self, template_code: str) -> str:
        """
        Add useful Jinja2 macros for common Django patterns
        """
        macros = []
        
        # Add macro if needed for pluralize
        if "pluralize" in template_code and "{# pluralize macro #}" not in template_code:
            macros.append("""
{# Pluralize macro for Jinja2 #}
{% macro pluralize(count, singular='', plural='s') %}
    {{ singular if count == 1 else plural }}
{% endmacro %}
""")
        
        if macros:
            return "\n".join(macros) + "\n" + template_code
        
        return template_code

    def improve_inheritance_chain(self, template_code: str) -> str:
        """
        Ensure proper template inheritance
        """
        improved = template_code
        
        # Ensure extends is first (after comments)
        lines = improved.split('\n')
        extends_line = None
        other_lines = []
        
        for line in lines:
            if '{% extends' in line:
                extends_line = line
            else:
                other_lines.append(line)
        
        if extends_line:
            # Find first non-comment line
            comments = []
            code = []
            for line in other_lines:
                if line.strip().startswith('{#') or line.strip().startswith('<!--'):
                    comments.append(line)
                else:
                    code.append(line)
            
            improved = "\n".join(comments + [extends_line] + code)
        
        return improved

    def validate_conversion(self, original: str, converted: str) -> Dict:
        """
        Validate templates conversion accuracy
        Returns: accuracy score and issues found
        """
        issues = []
        score = 100
        
        # Count template tags
        original_tags = len(re.findall(r"{%\s*\w+", original))
        converted_tags = len(re.findall(r"{%\s*\w+", converted))
        
        if original_tags != converted_tags:
            issues.append(f"Tag count mismatch: {original_tags} → {converted_tags}")
            score -= 15
        
        # Check for unconverted patterns
        if "{% load static %}" in converted:
            issues.append("Found unconverted load static tag")
            score -= 10
        
        if "forloop." in converted:
            issues.append("Found unconverted forloop variables")
            score -= 10
        
        # Check for Django filters not converted
        if "| capfirst" in converted or "| slugify" in converted:
            issues.append("Found Django-specific filters not converted")
            score -= 5
        
        # Count extends
        original_extends = len(re.findall(r"{%\s*extends", original))
        converted_extends = len(re.findall(r"{%\s*extends", converted))
        
        if original_extends != converted_extends:
            issues.append(f"Extends count mismatch: {original_extends} → {converted_extends}")
            score -= 10
        
        # Check for proper Jinja2 syntax
        if "{{ " in converted and " }}" not in converted:
            issues.append("Malformed Jinja2 variable syntax")
            score -= 20
        
        return {
            'accuracy_score': max(0, score),
            'issues': issues,
            'template_tags': converted_tags,
            'is_valid': len(issues) == 0 and score >= 80
        }
