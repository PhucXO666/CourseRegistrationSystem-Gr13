from datetime import datetime
from . import db

class RegistrationPeriod(db.Model):
    __tablename__ = 'registration_periods'
    
    period_id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(20), nullable=False)
    period_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('semester', 'period_name', name='unique_semester_period'),
    )
    
    def __repr__(self):
        return f'<RegistrationPeriod {self.period_name} ({self.semester})>'