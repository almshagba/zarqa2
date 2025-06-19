from flask import Flask, url_for
from routes.employee_routes import employee

app = Flask(__name__)
app.register_blueprint(employee)

with app.test_request_context():
    print("Directorate Employees URL:", url_for('employee.directorate_employees'))
    print("Add Directorate Employee URL:", url_for('employee.add_directorate_employee'))
    print("View Directorate Employee URL:", url_for('employee.view_directorate_employee', id=1))
    print("Edit Directorate Employee URL:", url_for('employee.edit_directorate_employee', id=1))
    print("Delete Directorate Employee URL:", url_for('employee.delete_directorate_employee', id=1)) 