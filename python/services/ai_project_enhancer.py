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

    def enhance_all_files(self, project_path: str) -> Dict:
        """
        Enhance all converted Python files in the project
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

        # Find all Python files in the project
        python_files = self._find_python_files(project_path)
        results['total_files'] = len(python_files)

        for file_path in python_files:
            try:
                # Read the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Determine file type
                relative_path = os.path.relpath(file_path, project_path)
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
                results['issues_found'].append({
                    'file': relative_path,
                    'error': str(e)
                })

        # Calculate average accuracy
        if results['accuracy_scores']:
            average = sum(results['accuracy_scores'].values()) / len(results['accuracy_scores'])
            results['average_accuracy'] = round(average, 2)

        return results

    def _find_python_files(self, project_path: str) -> List[str]:
        """Find all Python files in project"""
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and cache
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        return python_files

    def _determine_file_type(self, relative_path: str) -> str:
        """Determine file type from path"""
        if 'models' in relative_path:
            return 'models'
        elif 'views' in relative_path or 'routes' in relative_path:
            return 'views'
        elif 'forms' in relative_path:
            return 'forms'
        elif 'serializers' in relative_path:
            return 'serializers'
        elif 'urls' in relative_path:
            return 'urls'
        elif 'middleware' in relative_path:
            return 'middleware'
        elif 'utils' in relative_path or 'helpers' in relative_path:
            return 'utils'
        elif 'tests' in relative_path:
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
            # Return default if API call fails
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
        # Try direct JSON parsing first
        try:
            return json.loads(response_text)
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
        
        # Fallback: return default response with warning
        return {
            'enhanced_code': response_text,
            'accuracy_score': 75,
            'improvements': ['Could not parse structured response from AI']
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
