from datetime import datetime
from . import db

class ClassSection(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), db.ForeignKey('courses.course_code', ondelete='RESTRICT'), nullable=False)
    class_code = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    current_enrollment = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('Open', 'Canceled'), default='Open')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    schedule_info = db.Column(db.String(255))
    
    # Relationships
    registrations = db.relationship('Registration', backref='class_section', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('class_code', 'semester', name='unique_class_code'),
    )
    
    def __repr__(self):
        return f'<Class {self.class_code} ({self.course_code}) - {self.status}>'