"""
Advanced Routes Conversion Accuracy Improver
Handles complex Django view → Flask route conversion with high accuracy
"""

import re
from typing import Dict, List, Optional, Tuple


class RoutesAccuracyImprover:
    """
    Improves accuracy of Django views → Flask routes conversion
    Handles: request methods, decorators, responses, context, authentication
    """

    def __init__(self):
        self.method_mappings = self._build_method_mappings()
        self.response_patterns = self._build_response_patterns()
        self.decorator_mappings = self._build_decorator_mappings()

    def _build_method_mappings(self) -> Dict[str, str]:
        """Map Django view patterns to Flask"""
        return {
            'request.GET': 'request.args',
            'request.POST': 'request.form',
            'request.FILES': 'request.files',
            'request.method': 'request.method',
            'request.META': 'request.environ',
            'request.user': 'current_user',
        }

    def _build_response_patterns(self) -> Dict[str, str]:
        """Map Django response types to Flask"""
        return {
            'HttpResponse': 'Response',
            'JsonResponse': 'jsonify',
            'FileResponse': 'send_file',
            'StreamingHttpResponse': 'Response(..., streaming=True)',
            'HttpResponseRedirect': 'redirect',
            'HttpResponsePermanentRedirect': 'redirect(..., code=301)',
            'render': 'render_template',
            'render_to_response': 'render_template',
        }

    def _build_decorator_mappings(self) -> Dict[str, str]:
        """Map Django decorators to Flask"""
        return {
            '@login_required': '@login_required',
            '@permission_required': '@login_required  # Note: requires permission checking',
            '@cache_page': '@cache.cached(timeout=...)',
            '@csrf_protect': '# Flask has CSRF protection built-in',
            '@require_http_methods': '@app.route(..., methods=[...])',
            '@require_GET': '@app.route(..., methods=["GET"])',
            '@require_POST': '@app.route(..., methods=["POST"])',
            '@transaction.atomic': '# Use db.session for transactions',
        }

    def improve_function_based_views(self, django_code: str) -> str:
        """
        Improve function-based view conversion
        Handles: request parameter, decorators, responses
        """
        improved = django_code
        
        # Fix view function signature — remove `request` parameter (Flask uses the global `request`)
        improved = re.sub(
            r"def (\w+)\(request(?:,\s*([^)]+))?\)",
            lambda m: f"def {m.group(1)}({m.group(2) or ''}):" if m.group(2) else f"def {m.group(1)}():",
            improved
        )
        
        # Convert request handling
        improved = self._convert_request_handling(improved)
        
        # Convert responses
        improved = self._convert_responses(improved)
        
        # Convert decorators
        improved = self._convert_decorators(improved)
        
        # Fix GET/POST checks
        improved = self._fix_http_method_checks(improved)
        
        return improved

    def _convert_request_handling(self, code: str) -> str:
        """Convert Django request handling to Flask"""
        # Convert request.GET
        code = code.replace("request.GET.get(", "request.args.get(")
        code = code.replace("request.GET[", "request.args[")
        code = code.replace("request.POST.get(", "request.form.get(")
        code = code.replace("request.POST[", "request.form[")
        code = code.replace("request.FILES.get(", "request.files.get(")
        code = code.replace("request.FILES[", "request.files[")
        
        # Convert request.user
        code = code.replace("request.user", "current_user")
        
        # Convert request.method
        code = code.replace("request.method == 'GET'", "request.method == 'GET'")
        code = code.replace("request.method == 'POST'", "request.method == 'POST'")
        
        # Convert request.session
        code = code.replace("request.session[", "session[")
        code = code.replace("request.session.get(", "session.get(")
        
        return code

    def _convert_responses(self, code: str) -> str:
        """Convert Django responses to Flask"""
        # Convert HttpResponse
        code = re.sub(
            r"HttpResponse\(\s*([^)]+)\s*\)",
            r"Response(\1)",
            code
        )
        
        # Convert JsonResponse
        code = re.sub(
            r"JsonResponse\(\s*\{([^}]+)\}\s*\)",
            r"jsonify({\1})",
            code
        )
        
        # Convert render
        code = re.sub(
            r"render\(request,\s*['\"]([^'\"]+)['\"](?:,\s*\{([^}]*)\})?\)",
            lambda m: f"render_template('{m.group(1)}', {m.group(2) or ''})",
            code
        )
        
        # Convert redirect
        code = re.sub(
            r"redirect\('([^']+)'\)",
            r"redirect(url_for('\1'))",
            code
        )
        
        # Convert reverse URL lookup
        code = re.sub(
            r"reverse\('([^']+)'\)",
            r"url_for('\1')",
            code
        )
        
        return code

    def _convert_decorators(self, code: str) -> str:
        """Convert Django decorators to Flask"""
        for django_dec, flask_dec in self._build_decorator_mappings().items():
            code = code.replace(django_dec, flask_dec)
        
        # Fix CSRF decorator comment
        code = code.replace(
            "@csrf_protect  # Flask has CSRF protection built-in",
            "# @csrf_protect - Flask has CSRF protection via Flask-WTF"
        )
        
        return code

    def _fix_http_method_checks(self, code: str) -> str:
        """Fix if request.method checks"""
        # Convert if request.method == 'GET' patterns
        code = re.sub(
            r"if request\.method\s*==\s*['\"]GET['\"]:",
            "if request.method == 'GET':",
            code
        )
        
        code = re.sub(
            r"elif request\.method\s*==\s*['\"]POST['\"]:",
            "elif request.method == 'POST':",
            code
        )
        
        return code

    def improve_class_based_views(self, django_code: str) -> str:
        """
        Improve class-based view conversion
        Handles: dispatch, get/post methods, mixins
        """
        improved = django_code
        
        # Convert class-based view structure
        improved = self._convert_view_class_structure(improved)
        
        # Convert dispatch method
        improved = self._convert_dispatch(improved)
        
        # Convert get/post methods
        improved = self._convert_http_methods(improved)
        
        # Handle mixins
        improved = self._handle_mixins(improved)
        
        return improved

    def _convert_view_class_structure(self, code: str) -> str:
        """Convert Django class-based view to Flask"""
        # Convert View class
        code = code.replace("class MyView(View):", "# Use Flask view function or MethodView")
        code = code.replace("class MyView(TemplateView):", "# Use Flask route with render_template")
        
        # Convert to Flask MethodView pattern
        code = re.sub(
            r"class (\w+)\(View\):",
            r"class \1(MethodView):",
            code
        )
        
        code = re.sub(
            r"class (\w+)\(CreateView\):",
            lambda m: f"# {m.group(1)}: Create View\nclass {m.group(1)}(MethodView):",
            code
        )
        
        return code

    def _convert_dispatch(self, code: str) -> str:
        """Convert dispatch method"""
        # Replace dispatch with appropriate Flask handling
        code = code.replace(
            "def dispatch(self, request, *args, **kwargs):",
            "# Dispatch not needed in Flask - use route decorator instead"
        )
        
        return code

    def _convert_http_methods(self, code: str) -> str:
        """Convert get/post/put/delete methods"""
        # These should remain similar, just update context handling
        method_pattern = r"def (get|post|put|delete|patch)\(self, request(?:,\s*([^)]*))?\):"
        
        code = re.sub(
            method_pattern,
            lambda m: f"def {m.group(1).upper()}({m.group(2) or ''}):",
            code
        )
        
        # Fix context handling
        code = re.sub(
            r"context\[([^\]]+)\]\s*=\s*",
            r"context[\1] = ",
            code
        )
        
        return code

    def _handle_mixins(self, code: str) -> str:
        """Handle Django mixins conversion"""
        mixin_conversions = {
            'LoginRequiredMixin': '@login_required',
            'UserPassesTestMixin': '# Implement custom permission check',
            'PermissionRequiredMixin': '# Check permission before handling request',
            'FormMixin': '# Handle form manually',
        }
        
        for django_mixin, flask_equivalent in mixin_conversions.items():
            code = code.replace(django_mixin, f"# {django_mixin} → {flask_equivalent}")
        
        return code

    def improve_form_handling(self, django_code: str) -> str:
        """
        Improve form handling conversion
        Converts Django Forms to Flask-WTF
        """
        improved = django_code
        
        # Convert form instantiation
        improved = re.sub(
            r"form\s*=\s*MyForm\(\s*request\.POST",
            "form = MyForm() if request.method == 'POST' else MyForm()",
            improved
        )
        
        # Convert form validation
        improved = improved.replace(
            "if form.is_valid():",
            "if form.validate_on_submit():"
        )
        
        # Convert form data access
        improved = re.sub(
            r"form\.cleaned_data\[(['\"][^'\"]+['\"])\]",
            r"form.\1.data",
            improved
        )
        
        # Convert form errors
        improved = improved.replace(
            "form.errors",
            "form.errors"  # Same in both
        )
        
        return improved

    def improve_database_queries(self, django_code: str) -> str:
        """
        Improve database query conversion
        Converts Django ORM to SQLAlchemy
        """
        improved = django_code
        
        # Convert Model.objects.all()
        improved = re.sub(
            r"(\w+)\.objects\.all\(\)",
            r"db.session.query(\1).all()",
            improved
        )
        
        # Convert Model.objects.filter()
        improved = re.sub(
            r"(\w+)\.objects\.filter\(([^)]+)\)",
            r"db.session.query(\1).filter(\2)",
            improved
        )
        
        # Convert Model.objects.get()
        improved = re.sub(
            r"(\w+)\.objects\.get\(([^)]+)\)",
            r"db.session.query(\1).filter(\2).first()",
            improved
        )
        
        # Convert Model.objects.create()
        improved = re.sub(
            r"(\w+)\.objects\.create\(([^)]+)\)",
            lambda m: f"db.session.add({m.group(1)}({m.group(2)})); db.session.commit()",
            improved
        )
        
        # Convert QuerySet operations
        improved = improved.replace(".exists()", " is not None")
        improved = improved.replace(".count()", " | length")
        improved = improved.replace(".first()", ".first()")
        improved = improved.replace(".last()", "[-1]")
        
        return improved

    def improve_authentication(self, django_code: str) -> str:
        """
        Improve authentication handling
        Converts Django auth to Flask-Login
        """
        improved = django_code
        
        # Convert auth checks
        improved = improved.replace(
            "request.user.is_authenticated",
            "current_user.is_authenticated"
        )
        
        improved = improved.replace(
            "request.user.is_anonymous",
            "current_user.is_anonymous"
        )
        
        improved = improved.replace(
            "request.user.is_staff",
            "current_user.is_staff"
        )
        
        improved = improved.replace(
            "request.user.is_superuser",
            "current_user.is_admin or current_user.is_superuser"
        )
        
        # Convert permission checks
        improved = improved.replace(
            "request.user.has_perm(",
            "current_user.has_permission("
        )
        
        # Convert login/logout
        improved = improved.replace(
            "auth.login(request, user)",
            "login_user(user)"
        )
        
        improved = improved.replace(
            "auth.logout(request)",
            "logout_user()"
        )
        
        return improved

    def add_missing_imports(self, code: str) -> str:
        """Add necessary Flask imports"""
        needed_imports = []
        
        if "render_template" in code:
            needed_imports.append("from flask import render_template")
        if "jsonify" in code:
            needed_imports.append("from flask import jsonify")
        if "redirect" in code:
            needed_imports.append("from flask import redirect, url_for")
        if "request" in code:
            needed_imports.append("from flask import request")
        if "current_user" in code:
            needed_imports.append("from flask_login import current_user, login_required")
        if "db.session" in code:
            needed_imports.append("from flask_sqlalchemy import SQLAlchemy")
        
        import_section = "\n".join(set(needed_imports))
        
        if import_section and "from flask" not in code:
            code = import_section + "\n\n" + code
        
        return code

    def validate_conversion(self, original: str, converted: str) -> Dict:
        """
        Validate routes conversion accuracy
        Returns: accuracy score and issues found
        """
        issues = []
        score = 100
        
        # Count views
        original_views = len(re.findall(r"def \w+\(request", original))
        converted_views = len(re.findall(r"@app\.route|def \w+\(", converted))
        
        if original_views > converted_views:
            issues.append(f"View count mismatch: {original_views} → {converted_views}")
            score -= 20
        
        # Check for unconverted patterns
        if "request.GET" in converted or "request.POST" in converted:
            issues.append("Found unconverted request patterns")
            score -= 10
        
        if "HttpResponse" in converted:
            issues.append("Found unconverted response types")
            score -= 10
        
        if "model.objects" in converted:
            issues.append("Found unconverted Django ORM queries")
            score -= 15
        
        # Check for Flask patterns
        if "request.args" not in converted and "request.form" not in converted:
            if "request" in original:
                issues.append("Missing request parameter conversions")
                score -= 10
        
        return {
            'accuracy_score': max(0, score),
            'issues': issues,
            'view_count': converted_views,
            'is_valid': len(issues) == 0 and score >= 80
        }
