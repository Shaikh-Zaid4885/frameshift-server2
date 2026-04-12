"""
AI-Driven Full Project Validation and Quality Assurance
Validates entire converted Flask projects for production readiness
"""

import os
import ast
import re
from typing import Dict, List, Optional


class AIProjectValidator:
    """
    Comprehensive validation of converted Flask projects
    Ensures all components meet production-ready standards
    """

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.recommendations = []
        self.quality_score = 100

    def validate_complete_project(self, project_path: str) -> Dict:
        """
        Perform comprehensive project validation
        """
        validation_report = {
            'project_path': project_path,
            'overall_quality_score': 100,
            'is_production_ready': True,
            'components': {
                'models': {'valid': False, 'score': 0, 'issues': []},
                'views': {'valid': False, 'score': 0, 'issues': []},
                'templates': {'valid': False, 'score': 0, 'issues': []},
                'urls': {'valid': False, 'score': 0, 'issues': []},
                'forms': {'valid': False, 'score': 0, 'issues': []},
                'middleware': {'valid': False, 'score': 0, 'issues': []},
                'utils': {'valid': False, 'score': 0, 'issues': []},
            },
            'database': {'valid': False, 'score': 0, 'issues': []},
            'authentication': {'valid': False, 'score': 0, 'issues': []},
            'static_files': {'valid': False, 'score': 0, 'issues': []},
            'imports': {'valid': False, 'score': 0, 'issues': []},
            'syntax': {'valid': False, 'score': 0, 'issues': []},
            'recommendations': []
        }

        # Validate each component
        self._validate_models(project_path, validation_report)
        self._validate_views(project_path, validation_report)
        self._validate_templates(project_path, validation_report)
        self._validate_urls(project_path, validation_report)
        self._validate_forms(project_path, validation_report)
        self._validate_imports(project_path, validation_report)
        self._validate_syntax(project_path, validation_report)
        self._validate_authentication(project_path, validation_report)
        self._validate_database(project_path, validation_report)
        self._validate_static_files(project_path, validation_report)

        # Calculate overall score
        component_scores = []
        for component, data in validation_report['components'].items():
            if 'score' in data:
                component_scores.append(data['score'])
        
        for key in ['database', 'authentication', 'static_files', 'imports', 'syntax']:
            if key in validation_report and 'score' in validation_report[key]:
                component_scores.append(validation_report[key]['score'])

        if component_scores:
            overall_score = sum(component_scores) / len(component_scores)
            validation_report['overall_quality_score'] = round(overall_score, 2)
            validation_report['is_production_ready'] = overall_score >= 85

        return validation_report

    def _validate_models(self, project_path: str, report: Dict) -> None:
        """Validate SQLAlchemy models"""
        score = 0
        issues = []

        try:
            # Find models files
            models_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if 'models' in file and file.endswith('.py'):
                        models_files.append(os.path.join(root, file))

            if not models_files:
                issues.append("No model files found")
                score = 0
            else:
                # Check each models file
                proper_models = 0
                for model_file in models_files:
                    with open(model_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for SQLAlchemy patterns
                    if 'db.Model' in content or 'declarative_base()' in content:
                        proper_models += 1
                        # Check for proper fields
                        if 'db.Column' in content or 'Column(' in content:
                            score += 25
                        # Check for relationships
                        if 'db.relationship' in content or 'relationship(' in content:
                            score += 15
                        # Check for constraints
                        if 'db.ForeignKey' in content:
                            score += 10
                    else:
                        issues.append(f"Model file not using SQLAlchemy: {model_file}")

                if proper_models > 0:
                    score = min(score, 100)
                else:
                    score = 0

        except Exception as e:
            issues.append(f"Error validating models: {str(e)}")
            score = 0

        report['components']['models']['valid'] = score >= 70
        report['components']['models']['score'] = score
        report['components']['models']['issues'] = issues

    def _validate_views(self, project_path: str, report: Dict) -> None:
        """Validate Flask views/routes"""
        score = 0
        issues = []

        try:
            views_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if ('views' in file or 'routes' in file) and file.endswith('.py'):
                        views_files.append(os.path.join(root, file))

            if not views_files:
                issues.append("No view files found")
                score = 0
            else:
                for view_file in views_files:
                    with open(view_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for Flask patterns
                    if '@app.route' in content or '@bp.route' in content:
                        score += 30
                    elif 'def ' in content:
                        issues.append(f"Possible missing @app.route decorators in: {view_file}")
                    
                    # Check for request handling
                    if 'request.args' in content or 'request.form' in content or 'request.method' in content:
                        score += 20
                    
                    # Check for error handling
                    if 'try:' in content and 'except' in content:
                        score += 15
                    
                    # Check for response handling
                    if 'jsonify(' in content or 'render_template(' in content or 'redirect(' in content:
                        score += 15
                    
                    # Check for authentication
                    if '@login_required' in content or 'current_user' in content:
                        score += 10
                    
                    # Check for no Django patterns
                    if 'request.GET' in content or 'request.POST' in content:
                        issues.append(f"Found Django patterns in: {view_file}")
                        score = max(0, score - 10)

                score = min(score, 100)

        except Exception as e:
            issues.append(f"Error validating views: {str(e)}")
            score = 0

        report['components']['views']['valid'] = score >= 70
        report['components']['views']['score'] = score
        report['components']['views']['issues'] = issues

    def _validate_templates(self, project_path: str, report: Dict) -> None:
        """Validate Jinja2 templates"""
        score = 0
        issues = []

        try:
            templates_dir = os.path.join(project_path, 'templates')
            if os.path.exists(templates_dir):
                template_files = [f for f in os.walk(templates_dir) for f in os.listdir(f[0]) if f.endswith('.html')]
                
                if template_files:
                    # Spot check a few templates
                    for template_file in template_files[:5]:
                        with open(os.path.join(templates_dir, template_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for Jinja2 patterns
                        if '{{ ' in content or '{% ' in content:
                            score += 15
                        
                        # Check for template inheritance
                        if '{% extends' in content or '{% block' in content:
                            score += 10
                        
                        # Check for form rendering
                        if '{{ form' in content or '{% for' in content:
                            score += 10
                        
                        # Check for no Django patterns
                        if '{% load' in content or '{% static' in content or '{% url' in content:
                            issues.append(f"Found Django patterns in template: {template_file}")
                            score = max(0, score - 10)

                    score = min(score // len(template_files[:5]), 100) if template_files else 0
                else:
                    issues.append("No template files found")
                    score = 0
            else:
                issues.append("Templates directory not found")
                score = 0

        except Exception as e:
            issues.append(f"Error validating templates: {str(e)}")
            score = 0

        report['components']['templates']['valid'] = score >= 70
        report['components']['templates']['score'] = score
        report['components']['templates']['issues'] = issues

    def _validate_urls(self, project_path: str, report: Dict) -> None:
        """Validate URL configuration"""
        score = 0
        issues = []

        try:
            # Find urls/routes configuration files
            urls_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if 'urls' in file or ('config' in file and file.endswith('.py')):
                        if file.endswith('.py'):
                            urls_files.append(os.path.join(root, file))

            if urls_files:
                for urls_file in urls_files:
                    with open(urls_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for Flask patterns
                    if '@app.route' in content or 'app.route' in content:
                        score += 25
                    
                    if 'blueprint' in content or 'bp.' in content:
                        score += 15
                    
                    # Check for no Django patterns
                    if 'urlpatterns' in content or 'path(' in content or 're_path(' in content:
                        issues.append(f"Found Django patterns in: {urls_file}")
                        score = max(0, score - 10)

                score = min(score, 100)
            else:
                issues.append("No URL configuration file found")
                score = 20

        except Exception as e:
            issues.append(f"Error validating URLs: {str(e)}")
            score = 0

        report['components']['urls']['valid'] = score >= 70
        report['components']['urls']['score'] = score
        report['components']['urls']['issues'] = issues

    def _validate_forms(self, project_path: str, report: Dict) -> None:
        """Validate Flask-WTF forms"""
        score = 0
        issues = []

        try:
            forms_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if 'forms' in file and file.endswith('.py'):
                        forms_files.append(os.path.join(root, file))

            if forms_files:
                for forms_file in forms_files:
                    with open(forms_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for Flask-WTF patterns
                    if 'FlaskForm' in content or 'from wtforms' in content:
                        score += 30
                    
                    # Check for field definitions
                    if 'StringField' in content or 'IntegerField' in content:
                        score += 20
                    
                    # Check for validators
                    if 'validators.DataRequired' in content or 'DataRequired()' in content:
                        score += 15
                    
                    # Check for submit button
                    if 'SubmitField' in content:
                        score += 10
                    
                    # Check for no Django patterns
                    if 'forms.ModelForm' in content or 'from django' in content:
                        issues.append(f"Found Django patterns in: {forms_file}")
                        score = max(0, score - 15)

                score = min(score, 100)
            else:
                score = 50  # Forms are optional

        except Exception as e:
            issues.append(f"Error validating forms: {str(e)}")
            score = 0

        report['components']['forms']['valid'] = score >= 60
        report['components']['forms']['score'] = score
        report['components']['forms']['issues'] = issues

    def _validate_imports(self, project_path: str, report: Dict) -> None:
        """Validate imports across project"""
        score = 100
        issues = []

        try:
            python_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', 'venv']]
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))

            # Check each file
            for py_file in python_files:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Django imports that shouldn't be there
                if 'from django' in content and 'django.contrib.auth' not in content:
                    issues.append(f"Found Django import in: {py_file}")
                    score = max(0, score - 10)
                
                # Check for missing Flask imports in views
                if '@app.route' in content or '@bp.route' in content:
                    if 'from flask import' not in content and 'import flask' not in content:
                        issues.append(f"Missing Flask import in: {py_file}")
                        score = max(0, score - 5)

        except Exception as e:
            issues.append(f"Error validating imports: {str(e)}")
            score = 0

        report['imports']['valid'] = score >= 80
        report['imports']['score'] = score
        report['imports']['issues'] = issues

    def _validate_syntax(self, project_path: str, report: Dict) -> None:
        """Validate Python syntax"""
        score = 100
        issues = []

        try:
            python_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', 'venv']]
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))

            # Check each file
            total_files = len(python_files)
            valid_files = 0

            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to compile
                    compile(content, py_file, 'exec')
                    valid_files += 1
                except SyntaxError as e:
                    issues.append(f"Syntax error in {py_file}: {str(e)}")
                    score = max(0, score - 5)

            if total_files > 0:
                syntax_score = (valid_files / total_files) * 100
                score = min(score, syntax_score)

        except Exception as e:
            issues.append(f"Error validating syntax: {str(e)}")
            score = 0

        report['syntax']['valid'] = score >= 95
        report['syntax']['score'] = score
        report['syntax']['issues'] = issues

    def _validate_authentication(self, project_path: str, report: Dict) -> None:
        """Validate authentication setup"""
        score = 50  # Default if not found
        issues = []

        try:
            # Look for auth files/patterns
            found_auth = False
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if '@login_required' in content or 'flask_login' in content:
                            found_auth = True
                            score = 80
                            if 'current_user' in content:
                                score = 90
                            if 'login_user' in content or 'logout_user' in content:
                                score = 95

            if not found_auth:
                issues.append("No authentication setup found (may be optional)")
                score = 50

        except Exception as e:
            issues.append(f"Error validating authentication: {str(e)}")
            score = 0

        report['authentication']['valid'] = score >= 50
        report['authentication']['score'] = score
        report['authentication']['issues'] = issues

    def _validate_database(self, project_path: str, report: Dict) -> None:
        """Validate database configuration"""
        score = 50
        issues = []

        try:
            # Look for database configuration
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for SQLAlchemy configuration
                        if 'SQLAlchemy' in content or 'SQLALCHEMY_DATABASE_URI' in content:
                            score = 85
                            if 'db = SQLAlchemy' in content:
                                score = 90
                        
                        # Check for models
                        if 'db.Model' in content:
                            score = 95

            if score == 50:
                issues.append("No database configuration found")

        except Exception as e:
            issues.append(f"Error validating database: {str(e)}")
            score = 0

        report['database']['valid'] = score >= 70
        report['database']['score'] = score
        report['database']['issues'] = issues

    def _validate_static_files(self, project_path: str, report: Dict) -> None:
        """Validate static files setup"""
        score = 50
        issues = []

        try:
            static_dir = os.path.join(project_path, 'static')
            if os.path.exists(static_dir):
                static_files = os.listdir(static_dir)
                if static_files:
                    score = 80
                else:
                    issues.append("Static directory exists but is empty")
                    score = 60
            else:
                issues.append("No static directory found")
                score = 40

        except Exception as e:
            issues.append(f"Error validating static files: {str(e)}")
            score = 0

        report['static_files']['valid'] = score >= 50
        report['static_files']['score'] = score
        report['static_files']['issues'] = issues

    def generate_validation_report(self, validation_report: Dict) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("FLASK PROJECT VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall status
        score = validation_report['overall_quality_score']
        status = "✓ PRODUCTION READY" if validation_report['is_production_ready'] else "⚠ NEEDS REVIEW"
        report.append(f"Overall Quality Score: {score}% - {status}")
        report.append("")

        # Component scores
        report.append("COMPONENT VALIDATION SCORES:")
        report.append("-" * 80)
        for component, data in validation_report['components'].items():
            if 'score' in data:
                status_icon = "✓" if data['valid'] else "✗"
                report.append(f"  {status_icon} {component.upper()}: {data['score']}%")
                if data['issues']:
                    for issue in data['issues']:
                        report.append(f"     • {issue}")

        # Additional validations
        for key in ['database', 'authentication', 'static_files', 'imports', 'syntax']:
            if key in validation_report:
                data = validation_report[key]
                status_icon = "✓" if data['valid'] else "✗"
                report.append(f"  {status_icon} {key.upper()}: {data['score']}%")
                if data['issues']:
                    for issue in data['issues'][:3]:
                        report.append(f"     • {issue}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)
