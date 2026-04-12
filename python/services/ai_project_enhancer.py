"""
AI-Driven Full Project Accuracy Enhancement
Processes all converted files through AI for maximum accuracy
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AIProjectEnhancer:
    """
    Comprehensive AI-driven enhancement for entire converted projects
    Uses multiple AI providers for validation and optimization
    """

    def __init__(self, api_key: str, provider: str = 'gemini', model: Optional[str] = None):
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.enhanced_files = {}
        self.accuracy_scores = {}

    def enhance_all_files(self, project_path: str, progress_callback=None) -> Dict:
        """
        Enhance all converted project files in the project
        """
        results = {
            'enhanced_files': {},
            'accuracy_scores': {},
            'total_files': 0,
            'files_enhanced': 0,
            'average_accuracy': 0,
            'issues_found': [],
            'improvements_made': []
        }

        # Find all files to enhance in the project (.py, .html)
        files_to_enhance = self._find_project_files(project_path)
        results['total_files'] = len(files_to_enhance)

        if progress_callback:
            progress_callback(0, f"Starting AI enhancement of {results['total_files']} files")

        for i, file_path in enumerate(files_to_enhance):
            try:
                # Determine relative path and filename
                relative_path = os.path.relpath(file_path, project_path)
                filename = os.path.basename(file_path)

                # Report progress
                if progress_callback:
                    current_percentage = int((i / results['total_files']) * 100)
                    progress_callback(current_percentage, f"AI Reviewing: {filename}")

                # Read the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Determine file type
                file_type = self._determine_file_type(relative_path)

                # Enhance the file through AI
                enhanced_content, accuracy_score, improvements = self._enhance_file_with_ai(
                    content, file_type, relative_path
                )

                # Store results
                results['enhanced_files'][relative_path] = enhanced_content
                results['accuracy_scores'][relative_path] = accuracy_score
                results['files_enhanced'] += 1
                results['improvements_made'].extend(improvements)

            except Exception as e:
                # Attempt to get relative_path if it was set
                try:
                    rel_p = os.path.relpath(file_path, project_path)
                except:
                    rel_p = file_path
                
                results['issues_found'].append({
                    'file': rel_p,
                    'error': str(e)
                })

        # Calculate average accuracy
        if results['accuracy_scores']:
            average = sum(results['accuracy_scores'].values()) / len(results['accuracy_scores'])
            results['average_accuracy'] = round(average, 2)

        return results

    def _find_project_files(self, project_path: str) -> List[str]:
        """Find all project files for AI review (code, templates, config, docs)"""
        files_to_enhance = []
        # Define text-based extensions for AI review
        target_extensions = {
            '.py', '.html', '.txt', '.md', '.env', 
            '.sh', '.json', '.yml', '.yaml', '.example'
        }
        target_filenames = {'Procfile', 'Dockerfile', 'requirements.txt'}

        for root, dirs, files in os.walk(project_path):
            # Skip binary and cache dirs
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', 'venv', '.venv', 'env', 
                'node_modules', '.git', 'static', 'media', 'storage'
            ]]
            
            for file in files:
                ext = Path(file).suffix
                if ext in target_extensions or file in target_filenames:
                    files_to_enhance.append(os.path.join(root, file))

        return files_to_enhance

    def _determine_file_type(self, relative_path: str) -> str:
        """Categorize file for specialized AI prompting"""
        path_lower = relative_path.lower()
        
        if path_lower.endswith('requirements.txt'):
            return 'requirements'
        elif any(x in path_lower for x in ['procfile', 'dockerfile', '.sh', 'deploy']):
            return 'deployment'
        elif path_lower.endswith('.html'):
            return 'templates'
        elif '.env' in path_lower:
            return 'config'
        elif path_lower.endswith('.md') or 'readme' in path_lower:
            return 'docs'
        elif 'models' in path_lower:
            return 'models'
        elif 'views' in path_lower or 'routes' in path_lower:
            return 'views'
        elif 'forms' in path_lower:
            return 'forms'
        elif 'serializers' in path_lower:
            return 'serializers'
        elif 'urls' in path_lower:
            return 'urls'
        elif 'settings' in path_lower or 'config.py' in path_lower:
            return 'config_python'
        elif 'middleware' in path_lower:
            return 'middleware'
        elif 'utils' in path_lower or 'helpers' in path_lower:
            return 'utils'
        elif 'tests' in path_lower:
            return 'tests'
        else:
            return 'general'

    def _enhance_file_with_ai(self, content: str, file_type: str, file_path: str) -> Tuple[str, float, List[str]]:
        """
        Enhance a single file using AI
        Returns: enhanced_content, accuracy_score, improvements_list
        """
        
        # Build enhancement prompt based on file type
        prompt = self._build_enhancement_prompt(content, file_type, file_path)

        # Call AI API to enhance the file
        ai_response = self._call_ai_api(prompt)

        # Parse AI response
        enhanced_content = ai_response.get('enhanced_code', content)
        accuracy_score = ai_response.get('accuracy_score', 75)
        improvements = ai_response.get('improvements', [])

        # Safety: validate enhanced code compiles before accepting it
        if enhanced_content and enhanced_content != content and file_path.endswith('.py'):
            try:
                compile(enhanced_content, file_path, 'exec')
            except SyntaxError as e:
                # AI produced invalid code — keep original
                improvements.append(f'AI enhancement rejected: syntax error ({e})')
                enhanced_content = content
                accuracy_score = max(accuracy_score - 10, 0)

        # Safety: if AI returned empty or very short content, keep original
        if not enhanced_content or len(enhanced_content.strip()) < 10:
            enhanced_content = content
            improvements.append('AI returned empty/trivial content — kept original')

        return enhanced_content, accuracy_score, improvements

    def _build_enhancement_prompt(self, content: str, file_type: str, file_path: str) -> str:
        """Build AI enhancement prompt"""
        
        prompts = {
            'models': f"""You are a Django-to-Flask conversion expert. 
The following code is a converted Flask model file (originally Django).
Please ensure it:
1. Uses SQLAlchemy ORM correctly
2. Has proper field type mappings
3. Includes proper relationships (ForeignKey, ManyToMany, OneToOne)
4. Has proper inheritance if needed (Base class)
5. Includes proper constraints and indexes
6. Has proper validators
7. Includes proper docstrings
8. Follows Flask-SQLAlchemy conventions

Current code:
{content}

Provide:
1. Enhanced/corrected version of the code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}""",

            'views': f"""You are a Django-to-Flask conversion expert.
The following code is a converted Flask view/route file (originally Django).
Please ensure it:
1. Uses Flask best practices
2. Properly handles requests (GET, POST, PUT, DELETE)
3. Uses request.args for query params, request.form for POST data
4. Has proper error handling with try-catch
5. Uses flask-login for authentication
6. Properly serializes responses (JSON)
7. Includes proper docstrings
8. Uses blueprints correctly

Current code:
{content}

Provide:
1. Enhanced/corrected version of the code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}""",

            'forms': f"""You are a Django-to-Flask conversion expert.
The following code is a converted Flask form file (originally Django).
Please ensure it:
1. Uses Flask-WTF properly
2. Has proper field definitions
3. Includes all validators
4. Has proper validation methods
5. Includes error handling
6. Follows Flask conventions
7. Includes proper docstrings

Current code:
{content}

Provide:
1. Enhanced/corrected version of the code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}""",

            'urls': f"""You are a Django-to-Flask conversion expert.
The following code is a converted Flask URL/routes configuration file (originally Django).
Please ensure it:
1. Uses Flask @app.route() or blueprint routes correctly
2. Includes all HTTP methods properly
3. Has proper URL parameters
4. Uses url_for() correctly
5. Includes proper error handlers
6. Follows Flask conventions
7. Includes proper docstrings

Current code:
{content}

Provide:
1. Enhanced/corrected version of the code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}""",

            'requirements': f"""You are a Django-to-Flask conversion expert.
The following is a Python requirements.txt file.
Please:
1. Replace Django-specific packages with Flask equivalents (e.g., django-cors-headers -> flask-cors)
2. Ensure Flask, Flask-SQLAlchemy, Flask-Migrate, and Flask-WTF are included
3. Remove redundant Django-only packages
4. Keep core business logic libraries

Current file:
{content}

Provide:
1. Enhanced version of the requirements.txt
2. Accuracy score (0-100%)
3. List of changes made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 95, "improvements": ["replaced X with Y"]}}""",

            'deployment': f"""You are a Django-to-Flask conversion expert.
The following is a deployment config file (Procfile, Dockerfile, or script).
Please:
1. Fix entry points to use the Flask app object (usually 'app:app' or 'app:create_app()') instead of Django WSGI
2. Update environment variable names if necessary
3. Ensure Gunicorn/Waitress/etc. commands are correct for Flask

Current file:
{content}

Provide:
1. Enhanced version of the file
2. Accuracy score (0-100%)
3. List of changes made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 95, "improvements": ["updated WSGI entry point"]}}""",

            'docs': f"""You are a Django-to-Flask conversion expert.
The following is documentation (README or similar).
Please:
1. Update any Django-specific setup instructions to Flask equivalents (e.g., 'python manage.py runserver' -> 'flask run')
2. Fix mentions of Django paths or concepts to match the new Flask project structure
3. Maintain overall structure and content

Current file:
{content}

Provide:
1. Enhanced version of the document
2. Accuracy score (0-100%)
3. List of changes made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 95, "improvements": ["updated setup guide"]}}""",

            'config': f"""You are a Django-to-Flask conversion expert.
The following is a config or environment file (.env, .json, etc.).
Please:
1. Update key names from Django-style (DJANGO_SECRET_KEY) to Flask-style (SECRET_KEY)
2. Fix any Django-specific setting values
3. Ensure database URL formatting is correct for SQLAlchemy if present

Current file:
{content}

Provide:
1. Enhanced version of the file
2. Accuracy score (0-100%)
3. List of changes made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 95, "improvements": ["mapped env keys"]}}""",

            'config_python': f"""You are a Django-to-Flask conversion expert.
The following is a Python configuration file (config.py or settings.py).
Please:
1. Ensure it uses os.environ.get() for sensitive values
2. Verify SQLAlchemy configuration keys (SQLALCHEMY_DATABASE_URI, etc.)
3. Remove any leftover Django-specific configuration patterns
4. Ensure it follows Flask best practices for configuration objects

Current file:
{content}

Provide:
1. Enhanced version of the code
2. Accuracy score (0-100%)
3. List of changes made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 95, "improvements": ["updated SQLAlchemy keys"]}}""",

            'templates': f"""You are a Django-to-Flask conversion expert.
The following code is a converted Jinja2 template file (originally Django HTML).
Please ensure it:
1. Replaces all Django template tags with Jinja2 equivalents (e.g. {{% url ... %}} to {{% url_for ... %}})
2. Replaces Django static tags with url_for('static', filename=...)
3. Properly handles template inheritance (extends, block)
4. Uses proper Jinja2 filters and flow control
5. Maintains valid HTML structure
6. Fixes any leftover Django-specific syntax

Current code:
{content}

Provide:
1. Enhanced/corrected version of the HTML code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}""",

            'general': f"""You are a Django-to-Flask conversion expert.
The following is converted Flask code (originally Django).
Please enhance it to:
1. Follow Flask/Python best practices
2. Use proper imports
3. Include proper error handling
4. Add docstrings where missing
5. Ensure code quality and readability
6. Fix any conversion issues

Current code:
{content}

Provide:
1. Enhanced/corrected version of the code
2. Accuracy score (0-100%)
3. List of improvements made

Format as JSON:
{{"enhanced_code": "...", "accuracy_score": 85, "improvements": ["improvement1", "improvement2"]}}"""
        }

        return prompts.get(file_type, prompts['general'])

    def _call_ai_api(self, prompt: str) -> Dict:
        """Call AI API for enhancement"""
        try:
            if self.provider == 'gemini':
                return self._call_gemini_api(prompt)
            elif self.provider == 'openai':
                return self._call_openai_api(prompt)
            elif self.provider == 'claude':
                return self._call_claude_api(prompt)
            else:
                return self._call_custom_api(prompt)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"AI enhancement via '{self.provider}' failed for a file: {e}"
            )
            # Return default if API call fails — do NOT return enhanced_code
            # so the caller keeps the original content
            return {
                'accuracy_score': 75,
                'improvements': [f'AI enhancement failed: {str(e)}']
            }

    def _call_gemini_api(self, prompt: str) -> Dict:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model or 'gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from response using robust parsing
            return self._parse_ai_response(response_text)
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API"""
        try:
            import openai  # type: ignore
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model or 'gpt-4',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3
            )
            
            response_text = response['choices'][0]['message']['content']
            
            # Extract JSON from response using robust parsing
            return self._parse_ai_response(response_text)
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _call_claude_api(self, prompt: str) -> Dict:
        """Call Anthropic Claude API"""
        try:
            from anthropic import Anthropic  # type: ignore
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model or 'claude-3-opus-20240229',
                max_tokens=4096,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON from response using robust parsing
            return self._parse_ai_response(response_text)
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _call_custom_api(self, prompt: str) -> Dict:
        """Call custom API endpoint"""
        # This would call a custom API endpoint if configured
        return {
            'enhanced_code': '',
            'accuracy_score': 75,
            'improvements': ['Custom API not configured']
        }

    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Robustly parse AI response to extract JSON
        Handles nested braces and various JSON formats
        """
        import re

        # Strip markdown code fences if the AI wrapped the JSON in them
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', response_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)

        # Try direct JSON parsing first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object using bracket matching
        depth = 0
        start_idx = None
        
        for idx, char in enumerate(response_text):
            if char == '{':
                if depth == 0:
                    start_idx = idx
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    json_str = response_text[start_idx:idx + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue

        # Second pass: try to extract just the enhanced_code field with regex
        code_match = re.search(
            r'"enhanced_code"\s*:\s*"((?:[^"\\]|\\.)*)"',
            response_text, re.DOTALL
        )
        score_match = re.search(r'"accuracy_score"\s*:\s*(\d+)', response_text)
        if code_match:
            return {
                'enhanced_code': code_match.group(1).encode().decode('unicode_escape'),
                'accuracy_score': int(score_match.group(1)) if score_match else 75,
                'improvements': ['Extracted from partial AI response']
            }
        
        # Fallback: do NOT set enhanced_code so caller keeps original
        return {
            'accuracy_score': 75,
            'improvements': ['Could not parse structured response from AI — keeping original code']
        }

    def validate_flask_app(self, project_path: str) -> Dict:
        """
        Validate the entire Flask application
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'imports_valid': True,
            'syntax_valid': True,
            'structure_valid': True
        }

        # Check all Python files
        python_files = self._find_python_files(project_path)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Compile to check syntax
                compile(content, file_path, 'exec')
                
                # Check imports
                self._validate_imports(content, file_path, validation_results)
                
            except SyntaxError as e:
                validation_results['syntax_valid'] = False
                validation_results['is_valid'] = False
                validation_results['errors'].append({
                    'file': file_path,
                    'error': f'Syntax error: {str(e)}'
                })
            except Exception as e:
                validation_results['warnings'].append({
                    'file': file_path,
                    'warning': str(e)
                })

        return validation_results

    def _validate_imports(self, content: str, file_path: str, results: Dict) -> None:
        """Validate imports in file"""
        import re
        
        # Find all imports
        import_lines = re.findall(r'^\s*(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
        
        # Modules that should NOT appear in Flask code (Django patterns)
        django_modules = ['django', 'django.db', 'django.forms', 'django.views', 'django.urls']
        
        # Flask/SQLAlchemy standard imports to validate
        required_modules = {
            'flask': 'Flask framework',
            'flask_sqlalchemy': 'SQLAlchemy ORM',
            'flask_login': 'Authentication'
        }
        
        # Check for Django imports (should not exist)
        for imp in import_lines:
            for django_mod in django_modules:
                if django_mod in imp:
                    results['imports_valid'] = False
                    results['is_valid'] = False
                    results['errors'].append({
                        'file': file_path,
                        'error': f'Found Django import "{imp}" - should be Flask equivalent'
                    })
        
        # Check for critical imports in main app files
        if 'app' in file_path.lower() or 'main' in file_path.lower():
            if not any('flask' in imp for imp in import_lines):
                results['warnings'].append({
                    'file': file_path,
                    'warning': 'Main app file missing Flask import'
                })

    def generate_enhancement_report(self, results: Dict) -> str:
        """Generate comprehensive enhancement report"""
        report = []
        report.append("=" * 80)
        report.append("AI-DRIVEN FLASK PROJECT ENHANCEMENT REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total Files: {results['total_files']}")
        report.append(f"  Files Enhanced: {results['files_enhanced']}")
        report.append(f"  Average Accuracy: {results['average_accuracy']}%")
        report.append("")

        # Accuracy by file
        report.append("ACCURACY BY FILE:")
        report.append("-" * 80)
        for file_path, accuracy in sorted(results['accuracy_scores'].items()):
            status = "[PASS]" if accuracy >= 80 else "[WARN]"
            report.append(f"  {status} {file_path}: {accuracy}%")
        report.append("")

        # Improvements made
        if results['improvements_made']:
            report.append("IMPROVEMENTS MADE:")
            report.append("-" * 80)
            for improvement in results['improvements_made'][:20]:  # Show first 20
                report.append(f"  * {improvement}")
            if len(results['improvements_made']) > 20:
                report.append(f"  ... and {len(results['improvements_made']) - 20} more")
        report.append("")

        # Issues found
        if results['issues_found']:
            report.append("ISSUES FOUND:")
            report.append("-" * 80)
            for issue in results['issues_found']:
                report.append(f"  [FAIL] {issue['file']}: {issue['error']}")
        report.append("")

        # Overall status
        report.append("=" * 80)
        if results['average_accuracy'] >= 90:
            report.append("STATUS: [PASS] EXCELLENT - Flask project is production-ready")
        elif results['average_accuracy'] >= 80:
            report.append("STATUS: [PASS] GOOD - Flask project is mostly production-ready")
        elif results['average_accuracy'] >= 70:
            report.append("STATUS: [WARN] FAIR - Flask project needs some manual review")
        else:
            report.append("STATUS: [FAIL] POOR - Flask project needs significant manual work")
        report.append("=" * 80)

        return "\n".join(report)

    def save_enhanced_files(self, results: Dict, output_path: str) -> None:
        """Save all enhanced files to output path with validation"""
        saved_count = 0
        failed_count = 0
        
        for file_path, content in results['enhanced_files'].items():
            try:
                # Validate content before saving
                if not content or not isinstance(content, str):
                    results['issues_found'].append({
                        'file': file_path,
                        'error': 'Invalid content - skipped'
                    })
                    failed_count += 1
                    continue
                
                # Try to compile to check syntax
                try:
                    compile(content, file_path, 'exec')
                except SyntaxError as e:
                    results['issues_found'].append({
                        'file': file_path,
                        'error': f'Syntax error in enhanced code: {str(e)}'
                    })
                    failed_count += 1
                    continue
                
                # Save the file
                output_file = os.path.join(output_path, file_path)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                saved_count += 1
                
            except Exception as e:
                results['issues_found'].append({
                    'file': file_path,
                    'error': f'Failed to save: {str(e)}'
                })
                failed_count += 1
        
        results['files_saved'] = saved_count
        results['files_save_failed'] = failed_count
