from . import db

class Prerequisite(db.Model):
    __tablename__ = 'prerequisites'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), db.ForeignKey('courses.course_code', ondelete='CASCADE'), nullable=False)
    prerequisite_code = db.Column(db.String(20), db.ForeignKey('courses.course_code', ondelete='CASCADE'), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('course_code', 'prerequisite_code', name='unique_prerequisite'),
    )
    
    def __repr__(self):
        return f'<Prerequisite {self.prerequisite_code} -> {self.course_code}>'