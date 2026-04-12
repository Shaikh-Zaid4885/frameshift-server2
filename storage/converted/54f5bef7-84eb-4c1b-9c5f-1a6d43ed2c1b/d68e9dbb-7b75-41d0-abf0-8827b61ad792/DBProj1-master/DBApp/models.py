from extensions import db
from datetime import date # Only date is needed for default=date.today


class Student(db.Model):
    """
    Represents a student enrolled in the system.

    Attributes:
        id (int): Primary key, unique identifier for the student.
        name (str): Full name of the student. Cannot be null.
        email (str): Unique email address of the student. Cannot be null and must be unique.
        age (int): Age of the student. Must be between 0 and 120. Cannot be null.
        joined_date (date): Date when the student joined. Defaults to today's date. Cannot be null.
    """
    __tablename__ = 'student'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, doc="Unique identifier for the student.")

    # Core Fields
    name = db.Column(db.String(100), nullable=False, doc="Full name of the student.")
    _email = db.Column("email", db.String(254), nullable=False, unique=True, index=True, doc="Unique email address of the student.") # Renamed to _email to allow property setter
    _age = db.Column("age", db.Integer, nullable=False, doc="Age of the student. Must be between 0 and 120.") # Renamed to _age to allow property setter
    joined_date = db.Column(db.Date, nullable=False, default=date.today, doc="Date when the student joined.")

    # Relationships (Examples - not included directly as per original, but show how they would be structured)
    # One-to-Many relationship (e.g., a student has many courses):
    # courses = db.relationship('Course', backref='student', lazy=True, doc="Courses taken by the student.")
    # Note: 'Course' model would need to exist and have a ForeignKey to 'student.id'

    # Many-to-Many relationship (e.g., students and subjects):
    # student_subjects = db.Table('student_subjects',
    #     db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    #     db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
    # )
    # subjects = db.relationship('Subject', secondary=student_subjects, backref='students', lazy=True, doc="Subjects the student is enrolled in.")

    # Validators for age and email using properties
    @property
    def age(self):
        """
        Getter for the student's age.
        """
        return self._age

    @age.setter
    def age(self, value):
        """
        Setter for the student's age with validation.
        Ensures age is an integer and within a reasonable range (0-120).
        """
        if not isinstance(value, int):
            raise ValueError("Age must be an integer.")
        if not (0 <= value <= 120):
            raise ValueError("Age must be between 0 and 120.")
        self._age = value

    @property
    def email(self):
        """
        Getter for the student's email.
        """
        return self._email

    @email.setter
    def email(self, value):
        """
        Setter for the student's email with basic format validation.
        Ensures email is a string and contains '@' and a domain part.
        Database constraints (unique=True, nullable=False) handle further validation.
        """
        if not isinstance(value, str):
            raise ValueError("Email must be a string.")
        if "@" not in value or "." not in value.split("@")[-1]: # Basic format check
            raise ValueError("Invalid email format.")
        self._email = value

    def __repr__(self):
        """
        Returns a string representation of the Student object, primarily for debugging.
        """
        return f"<Student(id={self.id}, name='{self.name}', email='{self.email}')>"

    def __str__(self):
        """
        Returns a human-readable string representation of the Student object.
        """
        return f"{self.name} ({self.email})"
