"""
Middleware Converter
Converts Django middleware classes to Flask-equivalent hooks
"""

import re
from pathlib import Path
from typing import Dict, Any
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class MiddlewareConverter:
    """Convert Django middleware classes to Flask before/after request hooks"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.results = {
            'converted_files': [],
            'middleware_count': 0,
            'issues': []
        }

    def convert(self) -> Dict:
        """Find and convert all middleware.py files."""
        logger.info("Starting middleware conversion")

        middleware_files = FileHandler.find_files(str(self.django_path), 'middleware.py')
        middleware_files = [f for f in middleware_files if '__pycache__' not in str(f)]

        for mw_file in middleware_files:
            try:
                result = self._convert_file(mw_file)
                self.results['converted_files'].append(result)
            except Exception as e:
                logger.error(f"Failed to convert {mw_file}: {e}")
                self.results['issues'].append({
                    'file': str(mw_file),
                    'error': str(e)
                })

        return self.results

    def _convert_file(self, file_path: Path) -> Dict:
        source_code = FileHandler.read_file(str(file_path))
        converted_code, count = self._convert_middleware_code(source_code)
        self.results['middleware_count'] += count

        relative_path = file_path.relative_to(self.django_path)
        output_file = self.output_path / relative_path

        FileHandler.write_file(str(output_file), converted_code)

        return {
            'file': str(file_path),
            'output': str(output_file),
            'success': True,
            'middleware_count': count
        }

    def _convert_middleware_code(self, code: str) -> tuple[str, int]:
        count = 0
        
        # Imports
        code = "from flask import request, g, session, redirect, url_for\n\n" + code
        
        # 1. Convert __call__ or process_request
        # Django classes -> Flask functions or blueprint decorators
        
        def replace_middleware_class(match):
            nonlocal count
            class_name = match.group(1)
            body = match.group(2)
            count += 1
            
            # Simple mapping of Django logic to Flask hooks
            # This is very rough and usually requires manual review
            new_body = body
            new_body = re.sub(r'def\s+process_request\(self,\s*request\):', r'@app.before_request\ndef process_request():', new_body)
            new_body = re.sub(r'def\s+process_response\(self,\s*request,\s*response\):', r'@app.after_request\ndef process_response(response):', new_body)
            new_body = re.sub(r'def\s+process_view\(self,\s*request,\s*view_func,\s*view_args,\s*view_kwargs\):', r'@app.before_request\ndef process_view():', new_body)
            
            return (
                f"# Flask conversion of {class_name}\n"
                f"# NOTE: These hooks usually need to be registered on the app or a Blueprint.\n"
                f"{new_body}"
            )

        code = re.sub(r'class\s+(\w+)(?:\(object\))?:\s*\n((?:\s{4,}.*\n*)*)', replace_middleware_class, code)

        return code, count


__all__ = ['MiddlewareConverter']
