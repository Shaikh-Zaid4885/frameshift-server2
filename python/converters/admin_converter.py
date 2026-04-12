"""
Admin Converter
Converts Django admin.py files to Flask-Admin views
"""

import re
from pathlib import Path
from typing import Dict, Any
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class AdminConverter:
    """Convert Django admin.py to basic Flask-Admin views"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.results = {
            'converted_files': [],
            'total_admin_views': 0,
            'issues': []
        }

    def convert(self) -> Dict:
        """Find and convert all admin.py files."""
        logger.info("Starting admin conversion")

        admin_files = FileHandler.find_files(str(self.django_path), 'admin.py')
        admin_files = [f for f in admin_files if '__pycache__' not in str(f)]

        for admin_file in admin_files:
            try:
                result = self._convert_file(admin_file)
                self.results['converted_files'].append(result)
            except Exception as e:
                logger.error(f"Failed to convert {admin_file}: {e}", exc_info=True)
                self.results['issues'].append({
                    'file': str(admin_file.relative_to(self.django_path)),
                    'error': str(e)
                })

        return self.results

    def _convert_file(self, file_path: Path) -> Dict:
        source_code = FileHandler.read_file(str(file_path))

        converted_code, views_count = self._convert_admin_code(source_code)
        self.results['total_admin_views'] += views_count

        relative_path = file_path.relative_to(self.django_path)
        output_file = self.output_path / relative_path

        FileHandler.write_file(str(output_file), converted_code)

        return {
            'file': str(file_path),
            'output': str(output_file),
            'success': True,
            'views_count': views_count
        }

    def _convert_admin_code(self, code: str) -> tuple[str, int]:
        views_count = 0
        
        # 1. Imports
        code = re.sub(r'from django\.contrib import admin\n?', '', code)
        code = "from flask_admin.contrib.sqla import ModelView\nfrom extensions import db\n\n" + code

        # 2. Convert admin.site.register(Model)
        # We replace this with a comment block because Flask-Admin setup must 
        # happen at the app level. We generate the ModelView subclasses so they exist.
        
        def replace_basic_register(match):
            nonlocal views_count
            model_name = match.group(1)
            views_count += 1
            return (
                f"class {model_name}Admin(ModelView):\n"
                f"    pass\n\n"
                f"# TODO: Route this view in your extensions/init phase:\n"
                f"# admin.add_view({model_name}Admin({model_name}, db.session))\n"
            )

        code = re.sub(r'admin\.site\.register\((\w+)\)', replace_basic_register, code)

        # 3. Convert class ModelAdmin subclasses
        def replace_class_admin(match):
            nonlocal views_count
            class_name = match.group(1)
            model_admin = match.group(2)
            body = match.group(3)
            views_count += 1
            
            # Map Django admin fields to Flask-admin
            body = re.sub(r'list_display\s*=', 'column_list =', body)
            body = re.sub(r'search_fields\s*=', 'column_searchable_list =', body)
            body = re.sub(r'list_filter\s*=', 'column_filters =', body)
            body = re.sub(r'exclude\s*=', 'form_excluded_columns =', body)
            
            return f"class {class_name}(ModelView):\n{body}"

        code = re.sub(r'class\s+(\w+)\((admin\.ModelAdmin|admin\.UserAdmin)\):\s*\n((?:\s{4,}.*\n*)*)', replace_class_admin, code)

        # 4. Handle admin.site.register(Model, ModelAdmin)
        def replace_complex_register(match):
            model_name = match.group(1)
            admin_class = match.group(2)
            return (
                f"# TODO: Route this view in your extensions/init phase:\n"
                f"# admin.add_view({admin_class}({model_name}, db.session))\n"
            )

        code = re.sub(r'admin\.site\.register\((\w+),\s*(\w+)\)', replace_complex_register, code)

        # Clean remaining decorators
        code = re.sub(r'@admin\.register\(.*?\)\n', '', code)

        return code, views_count


__all__ = ['AdminConverter']
