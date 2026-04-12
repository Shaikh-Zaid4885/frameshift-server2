from flask_admin.contrib.sqla import ModelView
from extensions import db

from DBApp.models import Student

# Register your models here.
class StudentAdmin(ModelView):
    pass

# TODO: Route this view in your extensions/init phase:
# admin.add_view(StudentAdmin(Student, db.session))

