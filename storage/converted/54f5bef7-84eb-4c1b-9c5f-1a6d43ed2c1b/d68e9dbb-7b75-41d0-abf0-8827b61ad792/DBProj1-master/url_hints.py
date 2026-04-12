# application.py

from flask import Flask, Blueprint, render_template, request, abort, jsonify
from werkzeug.exceptions import HTTPException
import os

# --- 1. Blog Blueprint Definition (simulating blog/routes.py) ---
blog_bp = Blueprint('blog', __name__, url_prefix='/blog')
"""
A Blueprint for the blog section of the application.
This mimics Django's `include('blog.urls')` pattern by encapsulating
all blog-related routes under the `/blog` URL prefix.
"""

@blog_bp.route('/')
def blog_index():
    """
    Renders the blog index page.
    """
    # In a real application, 'posts' would be fetched from a database.
    # Using dummy data for demonstration.
    posts = [
        {'title': 'First Post', 'slug': 'first-post', 'content': 'This is the content of the first post.'},
        {'title': 'Second Post', 'slug': 'second-post', 'content': 'More blog content here.'}
    ]
    return render_template('blog/index.html', posts=posts)

@blog_bp.route('/<string:slug>/')
def blog_detail(slug):
    """
    Renders a single blog post based on its slug.

    Args:
        slug (str): The slug of the blog post.

    Returns:
        str: Rendered HTML page for the blog post.

    Raises:
        404 Not Found: If a blog post with the given slug is not found.
    """
    posts_data = {
        'first-post': {'title': 'First Post', 'content': 'This is the content of the first post.'},
        'second-post': {'title': 'Second Post', 'content': 'More blog content here.'}
    }
    post = posts_data.get(slug)
    if post: # Simulate fetching from DB
        return render_template('blog/detail.html', title=post['title'], content=post['content'])
    abort(404, description=f"Blog post '{slug}' not found")


# --- 2. Admin Blueprint Definition (simulating admin/routes.py or Flask-Admin setup) ---
# For Django's `/admin/` (view: site) usually maps to `django.contrib.admin.site`.
# In Flask, this is commonly implemented using Flask-Admin, or a custom Blueprint.
# We'll demonstrate with a simple custom blueprint for flexibility, mimicking a custom admin area.
# For a full-featured admin interface like Django's, Flask-Admin is the recommended library.
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
"""
A Blueprint for the administration section of the application.
This mimics Django's `admin.site` or a custom admin module, placed under the `/admin` URL prefix.
"""

@admin_bp.route('/')
def admin_dashboard():
    """
    Renders the admin dashboard.
    In a real application, this would require robust authentication and authorization.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Admin Dashboard</title></head>
    <body>
        <h1>Admin Dashboard</h1>
        <p>Welcome to the administration area!</p>
        <ul>
            <li><a href="/admin/users/">Manage Users</a></li>
            <li><a href="/admin/settings/">Application Settings</a></li>
        </ul>
    </body>
    </html>
    """

@admin_bp.route('/users/')
def admin_users():
    """
    Renders the user management page within the admin area.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Admin Users</title></head>
    <body>
        <h1>Admin Users</h1>
        <p>This is where you would manage users.</p>
        <p><a href="/admin/">Back to Dashboard</a></p>
    </body>
    </html>
    """

@admin_bp.route('/settings/')
def admin_settings():
    """
    Renders the application settings page within the admin area.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Admin Settings</title></head>
    <body>
        <h1>Admin Settings</h1>
        <p>Configure application settings here.</p>
        <p><a href="/admin/">Back to Dashboard</a></p>
    </body>
    </html>
    """


# --- 3. Main Application Factory ---
def create_app(test_config=None):
    """
    Creates and configures the Flask application instance using the application factory pattern.

    This function sets up the core Flask application, registers blueprints,
    configures error handling, and loads configurations.

    Args:
        test_config (dict, optional): Configuration for testing purposes.
                                     Defaults to None, in which case configuration
                                     is loaded from `config.py`.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_secret_key_please_change_in_production'),
        # Example database configuration
        # SQLALCHEMY_DATABASE_URI='sqlite:///instance/app.db',
        # SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, from 'config.py' when not testing
        # This file is not version-controlled and allows for environment-specific settings.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in (e.g., for unit tests)
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists for configuration and other instance-specific files
    try:
        os.makedirs(app.instance_path)
    except OSError: # Folder already exists
        pass

    # --- Register Blueprints ---
    # Blueprints modularize the application, equivalent to Django's `include()` in URLs.
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp)

    # --- Root/Index Route ---
    @app.route('/')
    def index():
        """
        Renders the main application index page.
        """
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Flask App Home</title></head>
        <body>
            <h1>Welcome to the Flask Application!</h1>
            <p>This is the main page.</p>
            <p>Check out the <a href='/blog/'>blog</a> or the <a href='/admin/'>admin</a> area.</p>
        </body>
        </html>
        """

    # --- Error Handling ---
    @app.errorhandler(404)
    def page_not_found(error):
        """
        Handles 404 Not Found errors.
        Provides a custom error page and a JSON response for API requests.

        Args:
            error (Exception): The exception object containing error details.

        Returns:
            tuple: A tuple containing the response (HTML or JSON) and the status code (404).
        """
        app.logger.warning(f"404 Not Found: {request.url} - {error.description}")
        # Check if the client prefers JSON (e.g., an API client)
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            response = jsonify({"error": "Not Found", "message": str(error.description)})
            response.status_code = 404
            return response
        # Otherwise, render an HTML error page
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handles 500 Internal Server Errors.
        Provides a custom error page and a JSON response for API requests.

        Args:
            error (Exception): The exception object containing error details.

        Returns:
            tuple: A tuple containing the response (HTML or JSON) and the status code (500).
        """
        app.logger.error(f"500 Internal Server Error: {request.url} - {error}", exc_info=True)
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            response = jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."})
            response.status_code = 500
            return response
        return render_template('errors/500.html', error=error), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Handles all HTTPException subclasses (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden).
        Provides a custom error page and a JSON response for API requests.

        Args:
            e (HTTPException): The HTTPException object.

        Returns:
            tuple: A tuple containing the response (HTML or JSON) and the status code.
        """
        app.logger.error(f"HTTP Exception: {e.code} - {request.url} - {e.description}")
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            response = jsonify({"code": e.code, "name": e.name, "description": e.description})
            response.status_code = e.code
            return response
        return render_template('errors/http_error.html', error=e), e.code

    return app

# To run the application directly (for development/testing):
# In a production setup, a WSGI server (like Gunicorn or uWSGI) would call create_app().
if __name__ == '__main__':
    # --- Setup for local execution (creating dummy template files) ---
    # In a real project, these files would be pre-existing under your 'templates' folder.
    template_paths = {
        'templates/blog': [
            ('index.html', "<!DOCTYPE html><html><head><title>Blog Index</title></head><body><h1>Blog Posts</h1><ul>{% for post in posts %}<li><a href='{{ url_for('blog.blog_detail', slug=post.slug) }}'>{{ post.title }}</a></li>{% endfor %}</ul></body></html>"),
            ('detail.html', "<!DOCTYPE html><html><head><title>{{ title }}</title></head><body><h1>{{ title }}</h1><p>{{ content }}</p><p><a href='{{ url_for('blog.blog_index') }}'>Back to blog</a></p></body></html>")
        ],
        'templates/errors': [
            ('404.html', "<!DOCTYPE html><html><head><title>Page Not Found</title></head><body><h1>404 - Page Not Found</h1><p>The page you are looking for could not be found.</p></body></html>"),
            ('500.html', "<!DOCTYPE html><html><head><title>Internal Server Error</title></head><body><h1>500 - Internal Server Error</h1><p>An unexpected error occurred on the server.</p></body></html>"),
            ('http_error.html', "<!DOCTYPE html><html><head><title>Error {{ error.code }}</title></head><body><h1>Error {{ error.code }} - {{ error.name }}</h1><p>{{ error.description }}</p></body></html>")
        ]
    }

    for dir_path, files in template_paths.items():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for filename, content in files:
            filepath = os.path.join(dir_path, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)

    # --- Run the Flask app ---
    app = create_app()
    app.run(debug=True)