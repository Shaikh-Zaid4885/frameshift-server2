from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user, login_user, logout_user
try:
    from .models import *
except ImportError:
    # TODO: Ensure models are defined and accessible (e.g., Item, User).
    pass

try:
    from .util import otp_generator, send_otp_email, validate_otp
except ImportError:
    otp_generator = None
    send_otp_email = None
    validate_otp = None
    # TODO: Implement utility functions for OTP if needed.

try:
    from haystack.query import SearchQuerySet
except ImportError:
    SearchQuerySet = None
    # TODO: Integrate with a Flask search solution if search functionality is needed.

try:
    from extensions import db
except ImportError:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    # TODO: If 'extensions.py' is not used, ensure 'db' is properly initialized with a Flask app instance.

app_bp = Blueprint('app', __name__)

@app_bp.route('/', methods=['GET'])
def home():
    item_list = []
    try:
        # Get all Item objects
        # Ensure Item model is defined and accessible for this query.
        item_list = Item.query.all()
    except Exception as e:
        # Log the error and provide a user-friendly message for database issues.
        print(f"Database error fetching items: {e}") # Log the error for debugging purposes
        flash("Could not load items at this time. Please try again later.", 'error')
        # For critical database errors that prevent rendering, consider:
        # from flask import abort
        # abort(500, description="Failed to retrieve items from the database.")
    
    return render_template('home.html', item_list=item_list)

@app_bp.route('/about', methods=['GET'])
def about():
    # Changed from a simple string return to rendering a template,
    # as is common practice for 'about' pages in Flask applications.
    # Assumes 'about.html' exists in the templates folder.
    return render_template('about.html')