from app import create_app
from models.user import User
from extensions import db

app = create_app()

with app.app_context():
    print("=" * 50)
    print("CREATING SAMPLE USERS")
    print("=" * 50)
    
    # Tạo hoặc cập nhật admin
    admin_user = User.query.filter_by(username='admin001').first()
    if not admin_user:
        admin_user = User(
            username='admin001',
            email='admin@example.com',
            full_name='Admin User',
            role='admin'
        )
        admin_user.set_password('password123')
        db.session.add(admin_user)
        print("✅ Created admin user: admin001 / password123")
    else:
        admin_user.set_password('password123')
        print("✅ Updated admin user password")
    
    # Tạo hoặc cập nhật students
    for i in range(1, 6):
        username = f'student{str(i).zfill(3)}'
        student = User.query.filter_by(username=username).first()
        if not student:
            student = User(
                username=username,
                email=f'student{i}@example.com',
                full_name=f'Student User {i}',
                role='student'
            )
            student.set_password('password123')
            db.session.add(student)
            print(f"✅ Created student user: {username} / password123")
        else:
            student.set_password('password123')
            print(f"✅ Updated student user: {username}")
    
    try:
        db.session.commit()
        print("=" * 50)
        print("🎉 Sample data created successfully!")
        
        # Hiển thị thông tin
        users = User.query.all()
        print(f"📊 Total users in database: {len(users)}")
        
        print("\n📋 List of users:")
        for user in users:
            print(f"  - {user.username} ({user.role}): {user.full_name}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")
    
    print("=" * 50)