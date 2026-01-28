from app import create_app
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🔄 Resetting all passwords to default...")
    
    # Danh sách user cần reset
    users_data = [
        {'username': 'admin001', 'email': 'admin@example.com', 'full_name': 'Admin User', 'role': 'admin'},
        {'username': 'student001', 'email': 'student@example.com', 'full_name': 'Student User', 'role': 'student'},
        {'username': 'student002', 'email': 'student002@example.com', 'full_name': 'Student User 2', 'role': 'student'},
        {'username': 'student003', 'email': 'student003@example.com', 'full_name': 'Student User 3', 'role': 'student'},
        {'username': 'student004', 'email': 'student004@example.com', 'full_name': 'Student User 4', 'role': 'student'},
        {'username': 'student005', 'email': 'student005@example.com', 'full_name': 'Student User 5', 'role': 'student'},
    ]
    
    for user_data in users_data:
        user = User.query.filter_by(username=user_data['username']).first()
        
        if user:
            # Reset password
            print(f"Resetting password for {user.username}...")
            user.password_hash = generate_password_hash('password123')
        else:
            # Tạo user mới
            print(f"Creating new user {user_data['username']}...")
            user = User(**user_data)
            user.password_hash = generate_password_hash('password123')
            db.session.add(user)
    
    try:
        db.session.commit()
        print("✅ All passwords have been reset to 'password123'")
        
        # Hiển thị thông tin user sau khi reset
        print("\n📋 Updated user list:")
        users = User.query.all()
        for user in users:
            print(f"  - {user.username} ({user.role}): Hash starts with {user.password_hash[:20]}...")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")