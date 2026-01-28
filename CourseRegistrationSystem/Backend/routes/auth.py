# routes/auth.py - KẾT HỢP CẢ HAI PHIÊN BẢN
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Trang đăng nhập - KẾT HỢP PHIÊN BẢN DEBUG VÀ PHIÊN BẢN GỐC
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Import trong hàm
        from models import User, Student, Admin
        from werkzeug.security import check_password_hash
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role
            
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.user_id).first()
                if student:
                    session['student_id'] = student.student_id
                return redirect(url_for('student.dashboard'))
            else:
                admin = Admin.query.filter_by(user_id=user.user_id).first()
                if admin:
                    session['admin_id'] = admin.admin_id
                return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
    
    # ====== DEBUG - CHỈ THÊM PHẦN NÀY VÀO PHIÊN BẢN GỐC ======
    print("\n" + "="*50)
    print("🔍 DEBUG TEMPLATE PATH:")
    current_dir = os.getcwd()
    print(f"1. Current directory: {current_dir}")
    
    # Kiểm tra nhiều đường dẫn
    possible_paths = [
        'templates/auth/login.html',
        './templates/auth/login.html',
        '../templates/auth/login.html',
        'Backend/templates/auth/login.html'
    ]
    
    for path in possible_paths:
        full_path = os.path.join(current_dir, path)
        exists = os.path.exists(full_path)
        print(f"2. {path}: {exists}")
        if exists:
            print(f"   → Full path: {full_path}")
    
    # Kiểm tra thư mục templates
    templates_dir = os.path.join(current_dir, 'templates')
    print(f"3. Templates directory exists: {os.path.exists(templates_dir)}")
    
    if os.path.exists(templates_dir):
        print("4. Files in templates:")
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                print(f"   - {os.path.join(root, file)}")
    print("="*50 + "\n")
    # ====== END DEBUG ======
    
    # Thử render template - GIỮ NGUYÊN PHẦN NÀY TỪ PHIÊN BẢN DEBUG
    try:
        return render_template('auth/login.html')
    except Exception as e:
        # Nếu lỗi, trả về HTML tạm thời
        return f'''
        <!DOCTYPE html>
        <html>
        <body style="padding: 50px; font-family: Arial;">
            <h2>🔧 DEBUG MODE - Template không tìm thấy</h2>
            <p><strong>Lỗi:</strong> {e}</p>
            <p><strong>Current dir:</strong> {current_dir}</p>
            <p><strong>Tìm kiếm file tại:</strong> {os.path.join(current_dir, 'templates', 'auth', 'login.html')}</p>
            <hr>
            <h3>Form đăng nhập tạm thời:</h3>
            <form method="POST" action="/auth/login">
                <input name="username" placeholder="Username" style="padding: 10px; margin: 5px;"><br>
                <input type="password" name="password" placeholder="Password" style="padding: 10px; margin: 5px;"><br>
                <button style="padding: 10px 20px; margin: 10px; background: #667eea; color: white; border: none;">
                    Đăng nhập
                </button>
            </form>
        </body>
        </html>
        '''

@auth_bp.route('/logout')
def logout():
    """
    Đăng xuất - GIỮ NGUYÊN TỪ PHIÊN BẢN GỐC
    """
    session.clear()
    return redirect(url_for('auth.login'))