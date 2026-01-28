from . import db

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    major = db.Column(db.String(100))
    enrollment_year = db.Column(db.Integer, nullable=False)
    
    # Relationships
    registrations = db.relationship('Registration', backref='student', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.student_id} - {self.user.full_name}>'