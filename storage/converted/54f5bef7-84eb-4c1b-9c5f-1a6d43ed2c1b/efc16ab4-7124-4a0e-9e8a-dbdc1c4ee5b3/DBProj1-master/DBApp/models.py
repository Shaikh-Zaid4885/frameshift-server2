from extensions import db


# Create your models here.

class Student(db.Model):
	__tablename__ = 'student'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(254), unique=True, nullable=False)
	age = db.Column(db.Integer, nullable=True)
	joined_date = db.Column(db.Date, nullable=False)

	def __repr__(self):
		return f"<Student {self.id}: {self.name} ({self.email})>"