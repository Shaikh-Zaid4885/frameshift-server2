# app.py
# This file demonstrates a conversion from Django URL hints to a Flask application structure.
# For larger applications, the blueprints and their routes would typically reside in
# separate modules (e.g., my_app/blog/routes.py, my_app/admin/routes.py)
# and registered in the main application factory.

from flask import Flask, Blueprint, render_template, abort, redirect, url_for, request
import os

# --- Blueprint Definitions ---
# These conceptually represent separate modules or 'apps' in Django terms.

# 1. Blog Blueprint
# Corresponds to Django's `path('blog/', include('blog.urls'))`
blog_bp = Blueprint('blog', __name__, url_prefix='/blog')
"""
Blueprint for handling blog-related routes.
Routes within this blueprint will automatically be prefixed with `/blog`.
"""

@blog_bp.route('/')
def blog_index():
    """
    View for the main blog page.
    This serves as the entry point for the blog section,
    similar to Django's blog app root URL.
    """
    return render_template('blog/index.html', title='Blog Home')

@blog_bp.route('/posts/<int:post_id>')
def blog_post_detail(post_id):
    """
    View to display a specific blog post.
    Demonstrates handling path converters and dynamic content.
    In a real application, this would fetch data from a database.
    """
    # Placeholder for database interaction
    mock_posts = {
        1: {"title": "First Blog Post", "content": "This is the content for the first blog post."},
        2: {"title": "Second Blog Post", "content": "Here's some content for the second blog post."},
    }
    post_data = mock_posts.get(post_id)

    if post_data is None:
        # Proper error handling: abort with 404 if post not found
        abort(404, description=f"Blog post with ID {post_id} not found.")

    return render_template(
        'blog/post_detail.html',
        title=post_data['title'],
        post_id=post_id,
        content=post_data['content']
    )

# Example of another route within the blog blueprint
@blog_bp.route('/about')
def blog_about():
    """
    View for the blog's about page.
    """
    return render_template('blog/about.html', title='About the Blog')


# 2. Admin Blueprint
# Corresponds to Django's `path('admin/', admin.site.urls)`
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
"""
Blueprint for handling administrative routes.
This replaces Django's built-in admin site with a custom Flask implementation
or an integration with a Flask-Admin like library.
Routes within this blueprint will automatically be prefixed with `/admin`.
"""

@admin_bp.route('/')
def admin_dashboard():
    """
    View for the main admin dashboard.
    This would be the landing page for the custom administration interface.
    Requires authentication/authorization in a real app.
    """
    return render_template('admin/dashboard.html', title='Admin Dashboard')

@admin_bp.route('/users')
def admin_users():
    """
    View for listing and managing users in the admin area.
    Requires authentication/authorization.
    """
    # In a real app, this would fetch user data from a database
    mock_users = [
        {'id': 1, 'username': 'admin_user', 'email': 'admin@example.com'},
        {'id': 2, 'username': 'blog_author', 'email': 'author@example.com'},
    ]
    return render_template('admin/users.html', title='Manage Users', users=mock_users)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """
    View for the admin login page.
    Handles both GET (display form) and POST (process login) requests.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Basic placeholder for login logic
        if username == 'admin' and password == 'password123': # NEVER do this in production
            # In a real app, set session, redirect to dashboard
            return redirect(url_for('admin.admin_dashboard'))
        else:
            # Show an error message
            return render_template('admin/login.html', title='Admin Login', error='Invalid credentials')

    return render_template('admin/login.html', title='Admin Login')


# --- Flask Application Factory ---

def create_app():
    """
    Flask application factory function.

    Initializes and configures the Flask application, registers blueprints,
    and sets up global error handlers.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # 1. Configuration Best Practices
    # Load configuration from environment variables or a config file.
    # SECRET_KEY is crucial for session security and should be strong and random.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'a_default_dev_secret_key_change_me_in_production!'), # TODO: Change this!
        # DEBUG should be False in production for security and performance.
        DEBUG=os.environ.get('FLASK_DEBUG') == '1' or False, # Default to False if FLASK_DEBUG not set
        # Add other configurations like database URI, etc.
        # SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///site.db')
        # TEMPLATES_AUTO_RELOAD=True, # Useful for development
    )

    # You might also load from an instance folder config for environment-specific settings
    # app.config.from_pyfile('config.py', silent=True)

    # 2. Register Blueprints
    # This is where the 'include()' patterns from Django are registered
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp)

    # 3. Main Application Routes (if any, not part of specific Django includes)
    @app.route('/')
    def home():
        """
        The main application home page.
        """
        return render_template('home.html', title='Welcome to Flask App')

    # Example: A redirect from an old URL (e.g., if you refactored a route)
    @app.route('/old-home')
    def old_home_redirect():
        """
        Redirects from an old URL path to the new home page.
        This can be useful for maintaining SEO or user experience after URL changes.
        """
        return redirect(url_for('home'))

    # 4. Global Error Handling
    # Catch-all error handlers for common HTTP errors
    @app.errorhandler(404)
    def page_not_found(error):
        """
        Handles 404 Not Found errors globally.
        Renders a custom 404 error page and logs a warning.
        """
        app.logger.warning(f"404 Not Found: {error.description}. Requested URL: {request.url}")
        return render_template('errors/404.html', error=error, title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handles 500 Internal Server Errors globally.
        Renders a custom 500 error page and logs the exception for debugging.
        """
        app.logger.exception(f"An internal server error occurred: {error.description}")
        return render_template('errors/500.html', error=error, title='Internal Server Error'), 500

    # You can add more specific error handlers as needed, e.g., for 403 Forbidden.
    # @app.errorhandler(403)
    # def forbidden(error):
    #     app.logger.warning(f"403 Forbidden: {error.description}. Requested URL: {request.url}")
    #     return render_template('errors/403.html', error=error, title='Forbidden'), 403

    return app

# 5. Entry Point for Running the Application (Development)
if __name__ == '__main__':
    # This block is primarily for local development using Flask's built-in server.
    # For production, a WSGI server (e.g., Gunicorn, uWSGI) would call `create_app()`
    # or `app` directly from a `wsgi.py` file.
    app = create_app()

    # Instructions for running and testing:
    print("\n--- Flask App Setup Instructions ---")
    print("To run this application, ensure you have the following directory and file structure:")
    print("my_flask_app/")
    print("├── app.py (this file)")
    print("└── templates/")
    print("    ├── home.html")
    print("    ├── blog/")
    print("    │   ├── index.html")
    print("    │   ├── post_detail.html")
    print("    │   └── about.html")
    print("    ├── admin/")
    print("    │   ├── dashboard.html")
    print("    │   ├── users.html")
    print("    │   └── login.html")
    print("    └── errors/")
    print("        ├── 404.html")
    print("        └── 500.html")
    print("\nCreate simple placeholder HTML files for these templates. For example, for templates/home.html:")
    print("```html")
    print("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>{{ title }}</title>\n</head>\n<body>\n    <h1>{{ title }}</h1>\n    <p>This is the home page.</p>\n    <ul>\n        <li><a href=\"{{ url_for('blog.blog_index') }}\">Go to Blog</a></li>\n        <li><a href=\"{{ url_for('admin.admin_dashboard') }}\">Go to Admin</a></li>\n    </ul>\n</body>\n</html>")
    print("```")
    print("\n--- Starting Flask Development Server ---")
    print("Access the application at: http://127.0.0.1:5000/")
    print("Blog section: http://127.0.0.1:5000/blog/")
    print("Admin section: http://127.0.0.1:5000/admin/")
    app.run(debug=True) # debug=True enables the debugger and auto-reloader for development