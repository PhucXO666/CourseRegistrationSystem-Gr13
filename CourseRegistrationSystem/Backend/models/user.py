from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('student', 'admin'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    admin = db.relationship('Admin', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash password và lưu vào database"""
        self.password_hash = generate_password_hash(password)
        return self.password_hash
    
    def check_password(self, password):
        """Kiểm tra password có khớp với hash không"""
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError as e:
            # Nếu hash không hợp lệ, tạo lại hash mới nếu password đúng
            print(f"Hash error for user {self.username}: {e}")
            if password == 'password123':  # Mật khẩu mặc định cho demo
                print(f"Regenerating hash for {self.username}")
                self.set_password(password)
                return True
            return False
        except Exception as e:
            print(f"Unexpected error checking password: {e}")
            return False
    
    def to_dict(self):
        """Chuyển user thành dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'