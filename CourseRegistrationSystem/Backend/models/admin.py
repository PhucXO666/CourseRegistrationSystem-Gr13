from . import db

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_code = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    department = db.Column(db.String(100))
    permission_level = db.Column(db.Enum('basic', 'advanced', 'super'), default='basic')
    
    # Relationships
    logs = db.relationship('AdminLog', backref='admin', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Admin {self.admin_code} - {self.user.full_name}>'