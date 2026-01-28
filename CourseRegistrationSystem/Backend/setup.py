from app import create_app
from models.user import User
from extensions import db

app = create_app()

with app.app_context():
    # Tạo database
    db.create_all()
    print("✅ Database tables created")
    
    # Tạo admin user mẫu
    admin = User.query.filter_by(username='admin001').first()
    if not admin:
        admin = User(
            username='admin001',
            email='admin@example.com',
            full_name='Admin User',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        print("✅ Created admin user: admin001 / password123")
    
    # Tạo student user mẫu
    student = User.query.filter_by(username='student001').first()
    if not student:
        student = User(
            username='student001',
            email='student@example.com',
            full_name='Student User',
            role='student'
        )
        student.set_password('password123')
        db.session.add(student)
        print("✅ Created student user: student001 / password123")
    
    db.session.commit()
    print("✅ All sample users created")
    
    # Kiểm tra
    user_count = User.query.count()
    print(f"📊 Total users in database: {user_count}")