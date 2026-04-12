from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, TextAreaField, SelectField, SubmitField, DecimalField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import Student

class StudentForm(FlaskForm):
	    # Note: Flask-WTF does not have ModelForm.
		model = Student
		fields = ['name','email','age','joined_date']


