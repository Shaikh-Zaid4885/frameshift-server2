"""
AI-Powered Conversion Enhancer using Google Gemini
Fixes critical issues that regex-based converters miss
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import concurrent.futures
from ..utils.logger import logger  # type: ignore
from ..providers import OpenAIProvider, GeminiProvider, ClaudeProvider, CustomProvider  # type: ignore


class AIEnhancer:
    """
    Uses Google Gemini to enhance converted Flask code
    Focuses on fixing specific high-impact issues
    """

    def __init__(self, api_key: str, provider: str = 'gemini', model: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = (provider or 'gemini').strip().lower()
        self.model_name = model
        self.endpoint = endpoint
        self.enhancements_applied: List[str] = []
        self.provider: Any = None
        self.enabled = bool(api_key)

        if not self.enabled:
            logger.warning("AI Enhancer disabled (missing API key)")
            return

        try:
            self.provider = self._create_provider()
            if hasattr(self.provider, 'enabled') and not self.provider.enabled:
                self.enabled = False
                logger.warning(f"AI provider '{self.provider_name}' is not ready; enhancer disabled")
                return
            logger.info(f"AI Enhancer initialized with provider: {self.provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AI provider '{self.provider_name}': {e}")
            self.enabled = False

    def _create_provider(self):
        if self.provider_name == 'openai':
            if OpenAIProvider is None:
                raise RuntimeError('OpenAI provider is unavailable in this runtime')
            return OpenAIProvider(
                api_key=self.api_key,
                model=self.model_name or 'gpt-4o',
                endpoint=self.endpoint or 'https://api.openai.com/v1'
            )

        if self.provider_name == 'gemini':
            if GeminiProvider is None:
                raise RuntimeError('Gemini provider is unavailable in this runtime')
            return GeminiProvider(
                api_key=self.api_key,
                model=self.model_name or 'gemini-2.5-flash',
                endpoint=self.endpoint
            )

        if self.provider_name == 'claude':
            if ClaudeProvider is None:
                raise RuntimeError('Claude provider is unavailable in this runtime')
            return ClaudeProvider(
                api_key=self.api_key,
                model=self.model_name or 'claude-3-5-sonnet-latest',
                endpoint=self.endpoint or 'https://api.anthropic.com/v1'
            )

        if self.provider_name == 'custom':
            if CustomProvider is None:
                raise RuntimeError('Custom provider is unavailable in this runtime')
            return CustomProvider(
                api_key=self.api_key,
                model=self.model_name or 'default-model',
                endpoint=self.endpoint or ''
            )

        raise ValueError(f"Unsupported AI provider: {self.provider_name}")

    def enhance_conversion(self, project_path: Path, models_result: Dict, views_result: Dict) -> Dict:
        """
        Main enhancement entry point
        Applies AI fixes to converted code
        """
        if not self.enabled:
            return {'enabled': False, 'applied': []}

        logger.info(f"Starting AI enhancement for project: {project_path}")

        models_files = list(project_path.rglob('models.py'))
        routes_files = list(project_path.rglob('routes.py'))

        all_files = []
        for pat in ['*.py', '*.html']:
            for file_path in project_path.rglob(pat):
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(ignore in file_path.parts for ignore in ['venv', 'env', '__pycache__', 'node_modules', 'instance', 'migrations']):
                    continue
                
                # Exclude standard boilerplate to heavily save AI API quota and time
                if file_path.name in ['__init__.py', 'manage.py', 'wsgi.py', 'asgi.py', 'apps.py', 'tests.py', 'conftest.py']:
                    continue

                all_files.append(file_path)

        generic_files = [f for f in all_files if f not in models_files and f not in routes_files]

        # Determine optimal worker count for better parallelization
        import os
        cpu_count = os.cpu_count() or 4
        max_workers = min(cpu_count - 1, 8)  # Use up to 8 workers for parallel AI processing
        logger.info(f"AI Enhancement: Using {max_workers} workers for file processing")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            model_futures = [executor.submit(self._process_single_model, f) for f in models_files]  # type: ignore
            route_futures = [executor.submit(self._process_single_route, f) for f in routes_files]  # type: ignore
            generic_futures = [executor.submit(self._process_generic_file, f) for f in generic_files]  # type: ignore
            concurrent.futures.wait(model_futures + route_futures + generic_futures)

        return {
            'enabled': True,
            'applied': self.enhancements_applied
        }

    def _process_single_model(self, models_file: Path):
        try:
            content = models_file.read_text(encoding='utf-8')

            logger.info(f"Using AI to verify and enhance {models_file}")

            # Use Gemini to fix it
            fixed_content = self._enhance_models_with_ai(content, models_file.name)

            if fixed_content and fixed_content != content:
                # Safety: validate enhanced code compiles before overwriting
                try:
                    compile(fixed_content, str(models_file), 'exec')
                except SyntaxError as e:
                    logger.warning(f"[AI] Rejecting enhanced models in {models_file.name}: syntax error: {e}")
                    return

                # Backup original
                backup_file = models_file.with_suffix('.py.backup')
                backup_file.write_text(content, encoding='utf-8')

                # Write fixed version
                models_file.write_text(fixed_content, encoding='utf-8')

                self.enhancements_applied.append(f"models:{models_file.name}")
                logger.info(f"[AI] Enhanced models in {models_file.name}")

        except Exception as e:
            logger.error(f"Error enhancing models in {models_file}: {e}")

    def _enhance_models_with_ai(self, content: str, filename: str) -> Optional[str]:
        """Use AI to properly enhance and verify converted Flask models"""

        prompt = f"""You are an expert at converting Django models to Flask-SQLAlchemy.

TASK: Verify and enhance this model file that was automatically converted from Django to Flask-SQLAlchemy.

CURRENT CODE:
```python
{content}
```

REQUIREMENTS:
1. Ensure all columns use proper SQLAlchemy syntax (e.g., db.Column) and the classes inherit from db.Model.
2. If `AbstractUser` or `AbstractBaseUser` was present, ensure it is fully replaced with `db.Model, UserMixin` from flask_login, including standard fields (id, password, email, first_name, last_name, is_active, etc.) and without Django-specific fields like USERNAME_FIELD.
3. Ensure proper foreign keys and relationships are correctly translated to SQLAlchemy syntax (db.ForeignKey, db.relationship).
4. Add `__tablename__` if missing or keep it consistent.
5. Provide ONLY the final fixed Python code. No explanations, no markdown blocks.

IMPORTANT: Return ONLY the fixed Python code. No explanations, no markdown code blocks, just pure Python code.
"""

        try:
            fixed_code = self.provider.generate_conversion(prompt).strip()

            # Remove markdown code blocks if present
            fixed_code = re.sub(r'^```python\s*\n?', '', fixed_code, flags=re.IGNORECASE)
            fixed_code = re.sub(r'\n?```\s*$', '', fixed_code)

            return fixed_code

        except Exception as e:
            logger.error(f"AI provider error enhancing model: {e}")
            return None

    def _process_single_route(self, routes_file: Path):
        try:
            content = routes_file.read_text(encoding='utf-8')

            logger.info(f"Using AI to verify and enhance {routes_file}")

            # Also find corresponding views.py if it exists
            views_file = routes_file.parent / 'views.py'
            views_content = None
            if views_file.exists():
                views_content = views_file.read_text(encoding='utf-8')

            # Use Gemini to implement routes
            implemented_content = self._enhance_routes_with_ai(
                content,
                views_content,
                routes_file.name
            )

            if implemented_content and implemented_content != content:
                # Safety: validate enhanced code compiles before overwriting
                try:
                    compile(implemented_content, str(routes_file), 'exec')
                except SyntaxError as e:
                    logger.warning(f"[AI] Rejecting enhanced routes in {routes_file.name}: syntax error: {e}")
                    return

                # Backup original
                backup_file = routes_file.with_suffix('.py.backup')
                backup_file.write_text(content, encoding='utf-8')

                # Write implemented version
                routes_file.write_text(implemented_content, encoding='utf-8')

                self.enhancements_applied.append(f"routes:{routes_file.name}")
                logger.info(f"[AI] Implemented routes in {routes_file.name}")

        except Exception as e:
            logger.error(f"Error implementing routes in {routes_file}: {e}")

    def _enhance_routes_with_ai(self, routes_content: str, views_content: Optional[str], filename: str) -> Optional[str]:
        """Use Gemini to properly enhance and verify converted Flask routes"""

        views_context = ""
        if views_content:
            views_context = f"""
ORIGINAL DJANGO VIEWS (for reference):
```python
{views_content}
```
"""

        prompt = f"""You are an expert at converting Django views to Flask routes.

TASK: Verify, enhance, and implement these Flask routes.

CURRENT FLASK ROUTES:
```python
{routes_content}
```

{views_context}

REQUIREMENTS:
1. Implement any missing logic left as placeholders (like `pass`, `return 'Hello from ...'`, generic `Operation completed` payloads, TODO comments).
2. Use proper Flask patterns (request.method, request.form, request.args, render_template, redirect, url_for, flash, session).
3. Ensure all database queries are proper SQLAlchemy syntax.
4. Add proper error handling.
5. Use Flask-Login decorators where appropriate (@login_required).
6. Verify and include necessary imports (flask, flask_login, app db).
7. If the file is already a correct Flask implementation, just return it unchanged or optimized, but ensure it works.
8. Do NOT invent placeholder model classes or mock query classes.
9. If a dependency cannot be resolved, keep a TODO comment instead of fabricating logic.

IMPORTANT: Return ONLY the final fixed Python code. No explanations, no markdown blocks.
"""

        try:
            implemented_code = self.provider.generate_conversion(prompt).strip()

            # Remove markdown code blocks if present
            implemented_code = re.sub(r'^```python\s*\n?', '', implemented_code, flags=re.IGNORECASE)
            implemented_code = re.sub(r'\n?```\s*$', '', implemented_code)

            return implemented_code

        except Exception as e:
            logger.error(f"AI provider error implementing routes: {e}")
            return None

    def _process_generic_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Use AI to verify it
            fixed_content = self._enhance_generic_file_with_ai(content, file_path.name)
            
            if fixed_content and fixed_content != content:
                # Safety: validate enhanced code compiles before overwriting (.py files)
                if file_path.suffix == '.py':
                    try:
                        compile(fixed_content, str(file_path), 'exec')
                    except SyntaxError as e:
                        logger.warning(f"[AI] Rejecting enhanced {file_path.name}: syntax error: {e}")
                        return

                # Safety: reject if AI returned something too short
                if len(fixed_content.strip()) < 10:
                    logger.warning(f"[AI] Rejecting enhanced {file_path.name}: content too short")
                    return

                # Backup original
                backup_file = file_path.with_suffix('.backup')
                backup_file.write_text(content, encoding='utf-8')

                # Write fixed version
                file_path.write_text(fixed_content, encoding='utf-8')

                self.enhancements_applied.append(f"generic:{file_path.name}")
                logger.info(f"[AI] Enhanced generic file {file_path.name}")

        except Exception as e:
            logger.error(f"Error enhancing {file_path}: {e}")

    def _enhance_generic_file_with_ai(self, content: str, filename: str) -> Optional[str]:
        prompt = f"""You are an expert at migrating Django projects to Flask.

TASK: Verify and adapt this file resulting from a Django-to-Flask conversion.
FILENAME: {filename}

CURRENT CODE:
```
{content}
```

REQUIREMENTS:
1. Identify any remaining Django-specific imports, classes, patterns (e.g., forms, middlewares, admin, signals, settings).
2. Convert them to proper Flask equivalents (e.g., Flask-WTF for forms, Flask-Admin configurations, standard Flask config patterns).
3. If it's an HTML template, verify and adapt Django template tags to Jinja2 natively (e.g., `{{% url 'name' %}}` to `{{{{ url_for('name') }}}}`).
4. If the file is already valid Flask/Jinja2 code or doesn't need changes, simply return it.
5. Provide ONLY the final updated code. No explanations, no markdown blocks.

IMPORTANT: Return ONLY the fixed code without any markdown wrappers.
"""
        try:
            fixed_code = self.provider.generate_conversion(prompt).strip()

            # Remove markdown code blocks if present
            fixed_code = re.sub(r'^```[a-z]*\s*\n?', '', fixed_code, flags=re.IGNORECASE)
            fixed_code = re.sub(r'\n?```\s*$', '', fixed_code)

            return fixed_code

        except Exception as e:
            logger.error(f"AI provider error enhancing generic file {filename}: {e}")
            return None

__all__ = ['AIEnhancer']
