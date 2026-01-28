from datetime import datetime
from . import db

class Registration(db.Model):
    __tablename__ = 'registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='RESTRICT'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('registered', 'dropped'), default='registered')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='unique_student_class'),
    )
    
    def __repr__(self):
        return f'<Registration {self.registration_id}: {self.student_id} -> Class {self.class_id} ({self.status})>'