from . import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    course_code = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    classes = db.relationship('ClassSection', backref='course', cascade='all, delete-orphan')
    prerequisites = db.relationship('Prerequisite', 
                                   foreign_keys='Prerequisite.course_code',
                                   backref='course',
                                   cascade='all, delete-orphan')
    required_for = db.relationship('Prerequisite',
                                  foreign_keys='Prerequisite.prerequisite_code',
                                  backref='prerequisite_course')
    
    def __repr__(self):
        return f'<Course {self.course_code}: {self.course_name}>'