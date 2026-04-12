"""
Forms Converter
Converts Django forms to Flask-WTF forms
"""

import ast
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class FormsConverter:
    """Convert Django forms to Flask-WTF forms"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.results = {
            'converted_files': [],
            'total_forms': 0,
            'issues': [],
            'warnings': []
        }

    def convert(self) -> Dict:
        """Find and convert all forms.py files."""
        logger.info("Starting forms conversion")

        form_files = FileHandler.find_files(str(self.django_path), 'forms.py')
        form_files = [f for f in form_files if '__pycache__' not in str(f)]

        for form_file in form_files:
            try:
                result = self._convert_file(form_file)
                self.results['converted_files'].append(result)
                self.results['total_forms'] += result.get('forms_count', 0)
            except Exception as e:
                logger.error(f"Failed to convert {form_file}: {e}", exc_info=True)
                self.results['issues'].append({
                    'file': str(form_file.relative_to(self.django_path)),
                    'error': str(e)
                })

        logger.info(f"Forms conversion complete. Converted {self.results['total_forms']} forms")
        return self.results

    def _convert_file(self, file_path: Path) -> Dict:
        """Convert a single forms.py file"""
        source_code = FileHandler.read_file(str(file_path))

        converted_code = self._convert_forms_code(source_code)

        relative_path = file_path.relative_to(self.django_path)
        output_file = self.output_path / relative_path

        FileHandler.write_file(str(output_file), converted_code)

        return {
            'file': str(file_path),
            'output': str(output_file),
            'success': True,
            'forms_count': converted_code.count('class ') - converted_code.count('class Meta')
        }

    def _convert_forms_code(self, code: str) -> str:
        """Convert Django forms syntax to Flask-WTF"""
        # 1. Replace imports
        code = self._convert_imports(code)

        # 2. Replace class inheritance
        code = re.sub(r'class\s+(\w+)\(forms\.ModelForm\):', r'class \1(FlaskForm):', code)
        code = re.sub(r'class\s+(\w+)\(forms\.Form\):', r'class \1(FlaskForm):', code)

        # 3. Convert fields
        code = self._convert_fields(code)

        # 4. Handle Meta classes
        code = self._convert_meta_classes(code)

        # 5. Convert clean_* methods to validate_* methods
        code = re.sub(r'def\s+clean_(\w+)\(self\):', r'def validate_\1(self, field):', code)

        return code

    def _convert_imports(self, code: str) -> str:
        """Replace Django forms imports with Flask-WTF"""
        # Remove django forms import
        code = re.sub(r'from django import forms\n?', '', code)
        code = re.sub(r'from django\.forms import .*\n?', '', code)

        # Add wtforms imports
        imports = (
            "from flask_wtf import FlaskForm\n"
            "from wtforms import StringField, PasswordField, BooleanField, IntegerField, "
            "DateField, TextAreaField, SelectField, SubmitField, DecimalField, FloatField\n"
            "from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError\n"
        )
        return imports + code

    def _convert_fields(self, code: str) -> str:
        """Map Django form fields to WTForms fields"""
        field_map = {
            'CharField': 'StringField',
            'EmailField': 'StringField',
            'PasswordField': 'PasswordField',
            'BooleanField': 'BooleanField',
            'IntegerField': 'IntegerField',
            'DecimalField': 'DecimalField',
            'FloatField': 'FloatField',
            'DateField': 'DateField',
            'TimeField': 'StringField',
            'DateTimeField': 'StringField',
            'URLField': 'StringField',
            'ImageField': 'StringField', # requires Flask-Uploads for true port, stubbing
            'FileField': 'StringField',
            'ChoiceField': 'SelectField',
            'MultipleChoiceField': 'SelectField'
        }

        for django_field, wtf_field in field_map.items():
            # forms.CharField -> StringField
            pattern = rf'forms\.{django_field}\('
            code = re.sub(pattern, f'{wtf_field}(', code)

        # Convert simple validators
        code = re.sub(r'required=False', '', code)
        code = re.sub(r'required=True', 'validators=[DataRequired()]', code)
        # wtforms expects empty string not '' if no other kwargs exist
        code = re.sub(r'StringField\(\)|StringField\(,\s*', 'StringField(', code)

        # Special case for EmailField validator mapping
        code = re.sub(r'EmailField\((.*?)\)', r'StringField(\1, validators=[DataRequired(), Email()])', code)

        # Replace widget=forms.PasswordInput with PasswordField
        code = re.sub(r'StringField\(.*?widget=forms\.PasswordInput.*?\)', r'PasswordField(', code)
        code = re.sub(r'StringField\(.*?widget=forms\.Textarea.*?\)', r'TextAreaField(', code)

        # Replace 'label=' with simple string first arg (WTForms standard)
        code = re.sub(r'(\w+Field)\(\s*label=[\'"](.*?)[\'"]', r'\1("\2"', code)

        return code

    def _convert_meta_classes(self, code: str) -> str:
        """Handle ModelForm Meta classes (convert to comment or structure)"""
        meta_pattern = r'class Meta:\s*\n((?:\s{4,}.*\n)*)'
        
        def process_meta(match):
            meta_body = match.group(1)
            model_match = re.search(r'model\s*=\s*(\w+)', meta_body)
            fields_match = re.search(r'fields\s*=\s*(.*)', meta_body)
            
            result = ["    # Note: Flask-WTF does not have ModelForm."]
            if model_match:
                result.append(f"    # TODO: Define fields manually from Model: {model_match.group(1)}")
            if fields_match:
                result.append(f"    # Original fields: {fields_match.group(1)}")
            
            return '\n'.join(result) + '\n'

        return re.sub(meta_pattern, process_meta, code)


__all__ = ['FormsConverter']
