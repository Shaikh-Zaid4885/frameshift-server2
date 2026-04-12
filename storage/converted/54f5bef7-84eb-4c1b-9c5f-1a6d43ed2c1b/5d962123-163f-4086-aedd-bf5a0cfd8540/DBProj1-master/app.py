import logging
from flask import Flask, jsonify, make_response
from extensions import db, migrate

# Import configuration mapping
from config import config

# Import blueprints
from DBApp.routes import DBApp_bp
from DBProj1.routes import DBProj1_bp

# Import models to ensure they're registered with SQLAlchemy metadata.
# This is crucial for db.create_all() to discover all model definitions.
# Ensure all model modules are imported here if they are not implicitly
# imported by your blueprints or other parts of the application startup.
import DBApp.models
# If DBProj1 also has its own models (e.g., in DBProj1/models.py), import them too:
# import DBProj1.models

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO, # Set to logging.DEBUG for more verbose output during development
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """
    Application factory function for DBProj1-master.

    Initializes the Flask application, loads configuration,
    registers extensions, blueprints, and sets up error handlers.

    Args:
        config_name (str): The name of the configuration to load
                           (e.g., 'development', 'testing', 'production').
                           Defaults to 'development'.

    Returns:
        Flask.app: The initialized Flask application instance.
    """
    app = Flask(__name__)

    # --- Configuration Loading ---
    if config_name not in config:
        logger.warning(f"Configuration '{config_name}' not found. Defaulting to 'development'.")
        config_name = 'development'
    
    app.config.from_object(config[config_name])
    logger.info(f"Loaded configuration: {config_name}")

    # --- Initialize Extensions ---
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        logger.info("SQLAlchemy and Flask-Migrate extensions initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize database extensions: {e}", exc_info=True)
        # In a critical failure like this, it's often better to re-raise
        # or exit if the application cannot function without the database.
        raise # Prevents app from starting if extensions fail

    # --- Register Blueprints ---
    app.register_blueprint(DBApp_bp, url_prefix='/DBApp')
    app.register_blueprint(DBProj1_bp, url_prefix='/DBProj1')
    logger.info("Blueprints 'DBApp_bp' and 'DBProj1_bp' registered.")

    # --- Database Table Creation (Development/Testing Convenience) ---
    # In a production environment, database tables should typically be managed
    # via migrations (e.g., `flask db upgrade`) rather than `db.create_all()`
    # at application startup. This approach is generally suitable for development and testing.
    # It must be called within an application context.
    with app.app_context():
        try:
            # Ensure models are imported BEFORE create_all() is called.
            # This has been handled by the module-level import above.
            db.create_all()
            logger.info("Database tables created/ensured (if not existing).")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}", exc_info=True)
            # If database table creation is essential for startup, consider re-raising.
            # raise # Uncomment to prevent app from starting if table creation fails

    # --- Error Handling ---
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handles 404 Not Found errors.
        Returns a JSON response for API consistency.
        """
        logger.warning(f"404 Not Found: {error}")
        return make_response(jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404)

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handles 500 Internal Server errors.
        Returns a JSON response for API consistency.
        """
        logger.exception(f"500 Internal Server Error: {error}") # Use exception to log traceback
        return make_response(jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred on the server."}), 500)

    @app.errorhandler(Exception)
    def catch_all_errors(error):
        """
        Handles any unhandled exceptions that bubble up to the application level.
        Returns a generic 500 JSON response.
        """
        logger.exception(f"Unhandled exception: {error}")
        return make_response(jsonify({"error": "Unhandled Exception", "message": "An unexpected error occurred."}), 500)


    # --- Root Route ---
    @app.route('/')
    def index():
        """
        Renders the application's welcome page.
        """
        return "Welcome to DBProj1-master!"

    return app

if __name__ == '__main__':
    # When running directly (e.g., `python app.py`), use the development configuration.
    # For production, consider using a WSGI server like Gunicorn and setting
    # environment variables (e.g., FLASK_ENV=production) or passing 'production'
    # as config_name directly in your deployment script.
    app = create_app('development')
    logger.info("Starting Flask application...")
    try:
        # `debug=app.config['DEBUG']` allows `DEBUG` to be controlled by the config.
        # In production, `DEBUG` should always be `False`.
        app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
    except Exception as e:
        logger.critical(f"Flask application failed to start: {e}", exc_info=True)
