from extensions import db


# Create your models here.

class Student(db.Model):
	__tablename__ = 'student'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(254), unique=True, nullable=False)
	age = db.Column(db.Integer)
	joined_date = db.Column(db.Date)

	def __str__(self):
		return self.name +"  "+ self.email