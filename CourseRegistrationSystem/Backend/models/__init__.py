# models/__init__.py
from extensions import db

# Import các model
from .user import User
from .student import Student
from .admin import Admin
from .course import Course
from .class_section import ClassSection
from .registration import Registration
from .registration_period import RegistrationPeriod
from .prerequisite import Prerequisite
from .admin_log import AdminLog

__all__ = [
    'db',
    'User',
    'Student',
    'Admin',
    'Course',
    'ClassSection',
    'Registration',
    'RegistrationPeriod',
    'Prerequisite',
    'AdminLog'
]