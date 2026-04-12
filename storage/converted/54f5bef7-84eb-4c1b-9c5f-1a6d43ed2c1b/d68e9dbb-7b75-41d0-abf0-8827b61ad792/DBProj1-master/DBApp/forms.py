from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, TextAreaField, SelectField, SubmitField, DecimalField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from datetime import date
# Assuming 'Student' is an SQLAlchemy model or similar ORM/ODM object
# that has a '.query' attribute for database lookups.
from .models import Student


class StudentForm(FlaskForm):
    """
    Form for creating or updating a student record in a Flask application.

    This form defines fields for student details (name, email, age, joined date)
    and includes comprehensive validation to ensure data integrity and user experience.
    It supports both creation of new students and updating existing ones, with
    special handling for email uniqueness during updates.
    """

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Name is required.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters long.')
        ]
    )

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Invalid email address format.'),
            Length(min=6, max=120, message='Email must be between 6 and 120 characters long.')
        ]
    )

    age = IntegerField(
        'Age',
        validators=[
            DataRequired(message='Age is required.'),
            NumberRange(min=5, max=100, message='Age must be between 5 and 100.') # Assuming reasonable age limits
        ]
    )

    joined_date = DateField(
        'Joined Date',
        format='%Y-%m-%d', # Ensure the date format is consistent
        validators=[
            DataRequired(message='Joined date is required.')
        ]
        # Optional: You can set a default value if needed, e.g., default=date.today
    )

    # Example of other potential fields a student might have (commented out):
    # grade = SelectField(
    #     'Grade Level',
    #     choices=[('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3')],
    #     validators=[DataRequired(message='Grade level is required.')]
    # )
    # bio = TextAreaField(
    #     'Biography',
    #     validators=[Length(max=500, message='Biography cannot exceed 500 characters.')]
    # )
    # is_active = BooleanField('Currently Active')

    submit = SubmitField('Save Student')

    def __init__(self, original_email=None, *args, **kwargs):
        """
        Initializes the StudentForm.

        Args:
            original_email (str, optional): The email of the student being edited.
                                            This is crucial for update scenarios to allow
                                            the student to keep their own email even if
                                            it already exists in the database.
                                            Defaults to None for new student creation.
        """
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        """
        Custom validator to ensure the email address is unique in the database.

        This method checks if the provided email already exists in the `Student` model.
        It explicitly allows the original email of the student being edited to pass
        validation, preventing unnecessary errors during updates.

        Args:
            email (wtforms.fields.StringField): The email field instance from the form.

        Raises:
            ValidationError: If the email already exists in the database and is not
                             the original email of the student being updated.
        """
        if email.data and email.data != self.original_email:
            # Assuming 'Student' is an ORM model with a 'query' attribute (e.g., SQLAlchemy)
            student = Student.query.filter_by(email=email.data).first()
            if student:
                raise ValidationError('That email address is already registered. Please use a different one.')
