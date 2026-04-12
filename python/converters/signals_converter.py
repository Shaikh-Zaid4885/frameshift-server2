"""
Signals Converter
Converts Django signals (receiver/post_save) to SQLAlchemy event listeners
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class SignalsConverter:
    """Convert Django signals to SQLAlchemy event listeners"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.results = {
            'converted_files': [],
            'signals_count': 0,
            'issues': []
        }

    def convert(self) -> Dict:
        """Find and convert all signals.py files."""
        logger.info("Starting signals conversion")

        signal_files = FileHandler.find_files(str(self.django_path), 'signals.py')
        signal_files = [f for f in signal_files if '__pycache__' not in str(f)]

        for signal_file in signal_files:
            try:
                result = self._convert_file(signal_file)
                self.results['converted_files'].append(result)
            except Exception as e:
                logger.error(f"Failed to convert {signal_file}: {e}")
                self.results['issues'].append({
                    'file': str(signal_file),
                    'error': str(e)
                })

        return self.results

    def _convert_file(self, file_path: Path) -> Dict:
        source_code = FileHandler.read_file(str(file_path))
        converted_code, count = self._convert_signals_code(source_code)
        self.results['signals_count'] += count

        relative_path = file_path.relative_to(self.django_path)
        output_file = self.output_path / relative_path

        FileHandler.write_file(str(output_file), converted_code)

        return {
            'file': str(file_path),
            'output': str(output_file),
            'success': True,
            'signals_count': count
        }

    def _convert_signals_code(self, code: str) -> tuple[str, int]:
        count = 0
        
        # 1. Imports
        code = re.sub(r'from django\.db\.models\.signals import .*\n?', '', code)
        code = re.sub(r'from django\.dispatch import receiver.*\n?', '', code)
        
        header = (
            "from sqlalchemy import event\n"
            "from extensions import db\n"
            "# TODO: Ensure models are imported before these listeners are registered\n\n"
        )
        
        # 2. @receiver(post_save, sender=Model)
        # -> @event.listens_for(Model, 'after_insert') and 'after_update'
        def replace_receiver(match):
            nonlocal count
            signal_type = match.group(1)
            sender = match.group(2)
            func_def = match.group(3)
            count += 1
            
            mapping = {
                'post_save': 'after_insert',
                'pre_save': 'before_insert',
                'post_delete': 'after_delete',
                'pre_delete': 'before_delete'
            }
            
            evt = mapping.get(signal_type, 'after_insert')
            
            # If it's post_save, we often want both insert and update
            if signal_type == 'post_save':
                return (
                    f"@event.listens_for({sender}, 'after_insert')\n"
                    f"@event.listens_for({sender}, 'after_update')\n"
                    f"{func_def.replace('instance', 'target').replace('created', 'is_insert')}"
                )
            
            return f"@event.listens_for({sender}, '{evt}')\n{func_def.replace('instance', 'target')}"

        code = re.sub(
            r'@receiver\((post_save|pre_save|post_delete|pre_delete),\s*sender=(\w+)\)\s*\n(def\s+\w+\(sender,\s*instance,.*?\):)',
            replace_receiver,
            code,
            flags=re.DOTALL
        )

        return header + code, count


__all__ = ['SignalsConverter']
