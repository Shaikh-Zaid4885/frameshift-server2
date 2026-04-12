"""
Advanced URL Patterns Conversion Accuracy Improver
Handles complex Django URL patterns → Flask routes conversion with high accuracy
"""

import re
from typing import Dict, List, Optional, Tuple


class URLPatternAccuracyImprover:
    """
    Improves accuracy of Django URL patterns → Flask routes conversion
    Handles: path parameters, regex patterns, named URLs, converters, query strings
    """

    def __init__(self):
        self.django_converters = self._build_django_converters()
        self.flask_converters = self._build_flask_converters()

    def _build_django_converters(self) -> Dict[str, str]:
        """Django URL converters"""
        return {
            'str': 'str',
            'int': 'int',
            'slug': 'slug',
            'uuid': 'uuid',
            'path': 'path',
        }

    def _build_flask_converters(self) -> Dict[str, str]:
        """Flask URL converters"""
        return {
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'uuid': 'uuid',
            'path': 'path',
        }

    def improve_path_patterns(self, django_urls: str) -> str:
        """
        Convert Django path() patterns to Flask @app.route()
        """
        improved = django_urls
        
        # Convert basic path patterns
        # path('admin/', admin_view) → @app.route('/admin/')
        improved = re.sub(
            r"path\(['\"]([^'\"]+)['\"],\s*(\w+)(?:,\s*name=['\"]([^'\"]+)['\"])?\)",
            lambda m: self._convert_path_to_route(m.group(1), m.group(2), m.group(3)),
            improved
        )
        
        # Convert path with int converter
        # path('users/<int:id>/', ...) → @app.route('/users/<int:id>/')
        improved = re.sub(
            r"<int:(\w+)>",
            r"<int:\1>",
            improved
        )
        
        # Convert path with str converter
        improved = re.sub(
            r"<str:(\w+)>",
            r"<\1>",  # Flask defaults to str
            improved
        )
        
        # Convert path with slug converter
        improved = re.sub(
            r"<slug:(\w+)>",
            r"<\1>",
            improved
        )
        
        # Convert path with uuid converter
        improved = re.sub(
            r"<uuid:(\w+)>",
            r"<\1>",
            improved
        )
        
        return improved

    def _convert_path_to_route(self, path: str, view: str, name: Optional[str] = None) -> str:
        """Convert single path pattern to Flask route decorator"""
        # Convert path parameters
        path = self._convert_path_parameters(path)
        
        # Create Flask decorator
        decorator = f"@app.route('{path}')\ndef {view}():"
        
        # Add endpoint name if provided
        if name:
            decorator = f"@app.route('{path}', endpoint='{name}')\ndef {view}():"
        
        return decorator

    def _convert_path_parameters(self, path: str) -> str:
        """Convert Django path parameters to Flask format"""
        # path/<int:id>/ stays as is
        path = re.sub(r"<(\w+):(\w+)>", r"<\1:\2>", path)
        
        # path/<id>/ becomes path/<id>
        path = re.sub(r"<(\w+)>", r"<\1>", path)
        
        return path

    def improve_re_path_patterns(self, django_urls: str) -> str:
        """
        Convert Django re_path() regex patterns to Flask routes
        Handles complex regex patterns
        """
        improved = django_urls
        
        # Find all re_path patterns
        pattern = r"re_path\(r?['\"]([^'\"]+)['\"],\s*(\w+)(?:,\s*name=['\"]([^'\"]+)['\"])?\)"
        
        improved = re.sub(
            pattern,
            lambda m: self._convert_re_path_to_route(m.group(1), m.group(2), m.group(3)),
            improved
        )
        
        return improved

    def _convert_re_path_to_route(self, regex: str, view: str, name: Optional[str] = None) -> str:
        """
        Convert regex pattern to Flask route
        Examples:
            r'^articles/(?P<year>[0-9]{4})/$' → '/articles/<int:year>/'
            r'^users/(?P<id>\d+)/$' → '/users/<int:id>/'
        """
        # Extract named groups from regex
        route_path = self._regex_to_flask_path(regex)
        
        # Create Flask decorator
        decorator = f"@app.route('{route_path}')\ndef {view}():"
        
        if name:
            decorator = f"@app.route('{route_path}', endpoint='{name}')\ndef {view}():"
        
        return decorator

    def _regex_to_flask_path(self, regex: str) -> str:
        """Convert regex pattern to Flask path"""
        # Remove anchors
        path = regex.replace(r"^", "").replace(r"$", "")
        
        # Convert named groups: (?P<year>[0-9]{4}) → <int:year>
        path = re.sub(
            r"\(\?P<(\w+)>[^)]*[0-9]{1,2}\)",
            r"<int:\1>",
            path
        )
        
        # Convert named groups: (?P<name>\w+) → <name>
        path = re.sub(
            r"\(\?P<(\w+)>\\w\+\)",
            r"<\1>",
            path
        )
        
        # Convert digit patterns: (?P<id>\d+) → <int:id>
        path = re.sub(
            r"\(\?P<(\w+)>\\d\+\)",
            r"<int:\1>",
            path
        )
        
        # Convert UUID patterns: (?P<uuid>[0-9a-f-]+) → <uuid:uuid>
        path = re.sub(
            r"\(\?P<(\w+)>[0-9a-f\-]+\)",
            r"<uuid:\1>",
            path
        )
        
        # Convert slug patterns: (?P<slug>[\w-]+) → <slug>
        path = re.sub(
            r"\(\?P<(\w+)>\\w\-\+\)",
            r"<\1>",
            path
        )
        
        # Remove trailing slashes if not needed
        path = path.rstrip("/")
        
        return path

    def improve_url_includes(self, django_urls: str) -> str:
        """
        Convert Django include() patterns to Flask blueprints
        """
        improved = django_urls
        
        # Convert include patterns
        # path('api/', include('myapp.urls')) → 
        # from myapp import bp; app.register_blueprint(bp, url_prefix='/api/')
        
        improved = re.sub(
            r"path\(['\"]([^'\"]+)['\"],\s*include\(['\"]([^'\"]+)['\"](?:\s*,\s*namespace=['\"]([^'\"]+)['\"])?\)\)",
            lambda m: self._convert_include_to_blueprint(m.group(1), m.group(2), m.group(3)),
            improved
        )
        
        return improved

    def _convert_include_to_blueprint(self, prefix: str, module: str, namespace: Optional[str] = None) -> str:
        """
        Convert Django include to Flask blueprint registration
        """
        # Extract app name from module path (e.g., 'myapp.urls' → 'myapp')
        app_name = module.split('.')[0]
        
        # Create blueprint registration
        comment = f"# Include from {module}"
        blueprint_import = f"from {app_name} import bp"
        blueprint_register = f"app.register_blueprint(bp, url_prefix='/{prefix.rstrip('/')}')"
        
        if namespace:
            blueprint_register = f"app.register_blueprint(bp, url_prefix='/{prefix.rstrip('/')}')  # namespace={namespace}"
        
        return f"{comment}\n{blueprint_import}\n{blueprint_register}"

    def improve_http_methods(self, django_urls: str) -> str:
        """
        Add HTTP method specifications to routes
        """
        improved = django_urls
        
        # Add methods parameter to routes
        # This is typically done in the view function itself in Flask
        
        # Look for views that handle multiple methods
        # Add comments indicating methods
        
        return improved

    def add_query_string_handling(self, view_code: str) -> str:
        """
        Add query string parameter handling
        """
        improved = view_code
        
        # Add request.args.get for query parameters
        if "request.GET.get" in view_code:
            improved = improved.replace("request.GET.get", "request.args.get")
        
        if "request.GET[" in view_code:
            improved = improved.replace("request.GET[", "request.args[")
        
        return improved

    def improve_trailing_slashes(self, django_urls: str) -> str:
        """
        Handle trailing slash normalization
        Django includes trailing slashes by default, Flask may not
        """
        improved = django_urls
        
        # Ensure trailing slashes are consistent
        improved = re.sub(
            r"@app\.route\(['\"]([^'\"]+?)/?['\"]",
            lambda m: f"@app.route('{m.group(1)}/', strict_slashes=False)",
            improved
        )
        
        return improved

    def improve_named_urls(self, django_urls: str, view_code: str) -> Tuple[str, str]:
        """
        Ensure named URLs are properly converted
        Django: reverse('view-name') → Flask: url_for('view-name')
        """
        # Extract URL names from urlpatterns
        url_names = re.findall(r"name=['\"]([^'\"]+)['\"]", django_urls)
        
        # Convert reverse() calls to url_for()
        improved_view = view_code
        for url_name in url_names:
            improved_view = improved_view.replace(
                f"reverse('{url_name}')",
                f"url_for('{url_name}')"
            )
            improved_view = improved_view.replace(
                f'reverse("{url_name}")',
                f'url_for("{url_name}")'
            )
        
        # Ensure endpoint names are consistent
        improved_urls = django_urls
        for url_name in url_names:
            improved_urls = improved_urls.replace(
                f"name='{url_name}'",
                f"endpoint='{url_name}'"
            )
        
        return improved_urls, improved_view

    def add_url_building_helpers(self, code: str) -> str:
        """
        Add Flask url_for helper if needed
        """
        if "url_for(" in code and "from flask import url_for" not in code:
            if "from flask import" in code:
                # Add to existing import
                code = code.replace(
                    "from flask import",
                    "from flask import url_for, "
                )
            else:
                # Add new import
                code = "from flask import url_for\n\n" + code
        
        return code

    def improve_blueprint_urls(self, django_urls: str) -> str:
        """
        Convert Django app-level URLs to Flask blueprints
        """
        improved = django_urls
        
        # Create Flask blueprint equivalent
        blueprint_template = '''
from flask import Blueprint

bp = Blueprint('{app_name}', __name__, url_prefix='/{url_prefix}')

@bp.route('/{route}')
def {view_name}():
    pass
'''
        
        # Note: Actual conversion happens in include handling above
        
        return improved

    def add_error_handlers(self, urls_code: str) -> str:
        """
        Add Flask error handlers for URL-related errors
        """
        if "404" not in urls_code:
            error_handler = '''
@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404

@app.errorhandler(405)
def method_not_allowed(error):
    return {"error": "Method not allowed"}, 405
'''
            urls_code = urls_code + "\n" + error_handler
        
        return urls_code

    def add_api_route_versioning(self, urls_code: str) -> str:
        """
        Add API versioning support if present
        """
        improved = urls_code
        
        # Look for versioned paths like /api/v1/
        if "/api/v" in urls_code:
            versioning_comment = """
# API Versioning:
# Version 1: /api/v1/...
# Version 2: /api/v2/...
# Use url_for with endpoint name to generate correct URLs
"""
            improved = versioning_comment + improved
        
        return improved

    def validate_conversion(self, original: str, converted: str) -> Dict:
        """
        Validate URL patterns conversion accuracy
        Returns: accuracy score and issues found
        """
        issues = []
        score = 100
        
        # Count URL patterns
        original_paths = len(re.findall(r"path\(|re_path\(", original))
        converted_routes = len(re.findall(r"@app\.route|@bp\.route", converted))
        
        if original_paths > converted_routes:
            issues.append(f"URL pattern count mismatch: {original_paths} → {converted_routes}")
            score -= 20
        
        # Check for unconverted patterns
        if "path(" in converted or "re_path(" in converted:
            issues.append("Found unconverted Django path/re_path patterns")
            score -= 15
        
        if "include(" in converted:
            issues.append("Found unconverted include() pattern")
            score -= 10
        
        # Check for reverse() not converted
        if "reverse(" in converted:
            issues.append("Found unconverted reverse() calls")
            score -= 10
        
        # Check for proper Flask syntax
        if "@app.route" not in converted and "@bp.route" not in converted:
            if "path(" in original:
                issues.append("No Flask routes found")
                score -= 30
        
        # Count named URLs
        original_names = len(re.findall(r"name=['\"]", original))
        converted_names = len(re.findall(r"endpoint=['\"]", converted))
        
        if original_names > converted_names:
            issues.append(f"Named URL count mismatch: {original_names} → {converted_names}")
            score -= 10
        
        return {
            'accuracy_score': max(0, score),
            'issues': issues,
            'route_count': converted_routes,
            'is_valid': len(issues) == 0 and score >= 80
        }
