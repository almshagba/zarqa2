from .main_routes import main
from .auth_routes import auth
from .employee_routes import employee
from .leave_routes import leave
from .school_routes import school
from .report_routes import report

__all__ = ['main', 'auth', 'leave', 'school', 'employee', 'report']