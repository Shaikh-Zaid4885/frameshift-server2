"""
Settings Converter
Parses Django settings.py and creates Flask config.py and .env.example
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from ..utils.file_handler import FileHandler
from ..utils.logger import logger


class SettingsConverter:
    """Extract Django settings and generate Flask configuration"""

    def __init__(self, django_path: str, output_path: str):
        self.django_path = Path(django_path)
        self.output_path = Path(output_path)
        self.results = {
            'converted_files': [],
            'config_generated': False,
            'env_generated': False,
            'issues': []
        }

    def convert(self) -> Dict:
        """Main entry point for settings conversion"""
        logger.info("Starting settings conversion")
        
        settings_path = self._find_settings_file()
        if not settings_path:
            self.results['issues'].append("Could not find Django settings.py")
            return self.results

        try:
            settings_content = FileHandler.read_file(str(settings_path))
            settings_data = self._parse_settings(settings_content)
            
            # 1. Generate config.py
            config_content = self._generate_config_py(settings_data)
            config_file = self.output_path / 'config.py'
            FileHandler.write_file(str(config_file), config_content)
            self.results['config_generated'] = True
            self.results['converted_files'].append(str(config_file))
            
            # 2. Generate .env.example
            env_content = self._generate_env_example(settings_data)
            env_file = self.output_path / '.env.example'
            FileHandler.write_file(str(env_file), env_content)
            self.results['env_generated'] = True
            self.results['converted_files'].append(str(env_file))
            
        except Exception as e:
            logger.error(f"Settings conversion failed: {e}")
            self.results['issues'].append(str(e))

        return self.results

    def _find_settings_file(self) -> Path:
        """Find the main settings.py in the Django project"""
        settings_files = FileHandler.find_files(str(self.django_path), 'settings.py')
        # Prefer the one not in a 'site-packages' or 'migrations' folder
        for f in settings_files:
            if 'site-packages' not in str(f) and 'migrations' not in str(f):
                return f
        return None

    def _parse_settings(self, content: str) -> Dict[str, Any]:
        """Extract key settings using regex"""
        data = {}
        
        # SECRET_KEY
        m = re.search(r"SECRET_KEY\s*=\s*['\"](.+?)['\"]", content)
        data['SECRET_KEY'] = m.group(1) if m else 'generate-a-secure-key-here'
        
        # DEBUG
        m = re.search(r"DEBUG\s*=\s*(True|False)", content)
        data['DEBUG'] = m.group(1) if m else 'True'
        
        # DATABASES
        # This is complex to parse via regex, so we look for patterns
        if 'postgresql' in content:
            data['DB_TYPE'] = 'postgresql'
        elif 'mysql' in content:
            data['DB_TYPE'] = 'mysql'
        else:
            data['DB_TYPE'] = 'sqlite'
            
        # Try to find DB name for sqlite
        m = re.search(r"['\"]NAME['\"]\s*:\s*BASE_DIR\s*/\s*['\"](.+?)['\"]", content)
        data['DB_NAME'] = m.group(1) if m else 'db.sqlite3'
        
        return data

    def _generate_config_py(self, data: Dict) -> str:
        db_uri = "os.environ.get('DATABASE_URL', 'sqlite:///dev.db')"
        if data['DB_TYPE'] == 'sqlite':
            db_uri = f"os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '{data['DB_NAME']}'))"

        return f"""import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '{data['SECRET_KEY']}')
    SQLALCHEMY_DATABASE_URI = {db_uri}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = {data['DEBUG']}
"""

    def _generate_env_example(self, data: Dict) -> str:
        return f"""# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY={data['SECRET_KEY']}

# Database
# For SQLite: sqlite:///dev.db
# For Postgres: postgresql://user:password@localhost:5432/dbname
DATABASE_URL=sqlite:///dev.db
"""

__all__ = ['SettingsConverter']
