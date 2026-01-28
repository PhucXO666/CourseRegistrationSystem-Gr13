from datetime import datetime
from . import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    admin_code = db.Column(db.String(20), db.ForeignKey('admins.admin_code', ondelete='RESTRICT'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminLog {self.log_id}: {self.admin_code} {self.action} {self.table_name}>'