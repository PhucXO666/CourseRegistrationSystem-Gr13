"""
Backend/app.py - Main Flask Application
Course Registration System
KẾT HỢP CẢ HAI PHIÊN BẢN
"""
import os
import sys
from functools import wraps

# Thêm đường dẫn hiện tại vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_file
    from werkzeug.security import check_password_hash
    print("✅ Flask and dependencies imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️ Please install dependencies: pip install flask werkzeug")
    sys.exit(1)

# Import local modules
try:
    from config import Config
    from extensions import db
    from models.user import User
    print("✅ Local modules imported successfully")
except ImportError as e:
    print(f"❌ Local import error: {e}")
    print("⚠️ Please check your project structure")
    sys.exit(1)

def create_app():
    """
    Create and configure the Flask application
    """
    # Xác định đường dẫn templates
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    
    # Kiểm tra và tạo thư mục templates nếu chưa có
    if not os.path.exists(template_dir):
        os.makedirs(template_dir, exist_ok=True)
        print(f"✅ Created templates directory: {template_dir}")
    
    # Tạo Flask app
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=os.path.join(base_dir, 'static'))
    
    # Load configuration
    app.config.from_object(Config)
    
    # Khởi tạo database
    db.init_app(app)
    
    # ==================== CONTEXT PROCESSORS ====================
    
    @app.context_processor
    def inject_user():
        """
        Inject current_user variable into all templates
        """
        user_info = {}
        if 'user_id' in session:
            user_info = {
                'current_user': {
                    'is_authenticated': True,
                    'id': session.get('user_id'),
                    'username': session.get('username'),
                    'full_name': session.get('full_name'),
                    'role': session.get('role'),
                    'email': session.get('email')
                }
            }
        else:
            user_info = {
                'current_user': {
                    'is_authenticated': False
                }
            }
        return user_info
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def home():
        """
        Home page - redirect to login or dashboard
        """
        # Nếu đã đăng nhập, chuyển đến dashboard tương ứng
        if 'user_id' in session:
            role = session.get('role')
            if role == 'admin':
                return redirect('/admin/dashboard')
            elif role == 'student':
                return redirect('/student/dashboard')
        
        # Nếu chưa đăng nhập, chuyển đến trang login
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Unified login page for both admin and student
        """
        # Nếu đã đăng nhập, chuyển hướng đến dashboard tương ứng
        if 'user_id' in session:
            role = session.get('role')
            if role == 'admin':
                return redirect('/admin/dashboard')
            elif role == 'student':
                return redirect('/student/dashboard')
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember')
            
            print(f"[LOGIN ATTEMPT] Username: {username}")
            
            # Kiểm tra input
            if not username or not password:
                flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!', 'danger')
                return render_template('login.html')
            
            # Tìm user trong database
            user = User.query.filter_by(username=username).first()
            
            if user:
                print(f"[LOGIN] User found: {user.username}, Role: {user.role}")
                
                try:
                    # Kiểm tra mật khẩu
                    if user.check_password(password):
                        print("[LOGIN] Password correct!")
                        
                        # Lưu thông tin vào session
                        session['user_id'] = user.user_id
                        session['username'] = user.username
                        session['role'] = user.role
                        session['full_name'] = user.full_name
                        session['email'] = user.email
                        
                        # Set session expiration
                        session.permanent = bool(remember)
                        
                        # Lưu thay đổi nếu có (trong trường hợp regenerate hash)
                        try:
                            db.session.commit()
                        except:
                            db.session.rollback()
                        
                        # Redirect theo role
                        if user.role == 'admin':
                            flash(f'Đăng nhập thành công! Chào mừng quản trị viên {user.full_name}!', 'success')
                            print("[REDIRECT] To admin dashboard")
                            return redirect('/admin/dashboard')
                        elif user.role == 'student':
                            flash(f'Đăng nhập thành công! Chào mừng sinh viên {user.full_name}!', 'success')
                            print("[REDIRECT] To student dashboard")
                            return redirect('/student/dashboard')
                        else:
                            flash('Vai trò người dùng không hợp lệ!', 'danger')
                    else:
                        print("[LOGIN] Password incorrect!")
                        flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
                        
                except Exception as e:
                    print(f"[LOGIN ERROR] {e}")
                    flash('Có lỗi xảy ra khi xác thực. Vui lòng thử lại!', 'danger')
            else:
                print(f"[LOGIN] User not found: {username}")
                flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """
        Logout user and clear session
        """
        username = session.get('username', 'Unknown')
        session.clear()
        flash(f'Bạn đã đăng xuất thành công. Tạm biệt {username}!', 'info')
        return redirect(url_for('login'))
    
    # ==================== AUTH DECORATORS ====================
    
    def login_required(f):
        """
        Decorator to require login for a route
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(required_role):
        """
        Decorator to require specific role for a route
        """
        def decorator(f):
            @wraps(f)
            @login_required
            def decorated_function(*args, **kwargs):
                current_role = session.get('role')
                if current_role != required_role:
                    flash('Bạn không có quyền truy cập trang này!', 'danger')
                    
                    # Redirect về dashboard tương ứng với role hiện tại
                    if current_role == 'admin':
                        return redirect('/admin/dashboard')
                    elif current_role == 'student':
                        return redirect('/student/dashboard')
                    else:
                        return redirect(url_for('logout'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # ==================== DASHBOARD ROUTES ====================
    # GIỮ NGUYÊN TỪ PHIÊN BẢN ĐẦU TIÊN
    
    @app.route('/admin/dashboard')
    @role_required('admin')
    def admin_dashboard():
        """
        Admin dashboard
        """
        user_info = {
            'username': session.get('username'),
            'full_name': session.get('full_name'),
            'role': session.get('role'),
            'email': session.get('email')
        }
        
        # Thêm thông tin cho admin dashboard
        dashboard_info = {
            'total_students': 1250,
            'total_courses': 85,
            'active_registrations': 2,
            'pending_requests': 12,
            'recent_activities': [
                {'action': 'Mở lớp CS101-01', 'time': '2 giờ trước'},
                {'action': 'Import sinh viên', 'time': 'Hôm qua'},
            ]
        }
        
        return render_template('admin/dashboard.html',
                             current_user=user_info,
                             **user_info,
                             **dashboard_info)
    
    # ==================== DEBUG/UTILITY ROUTES ====================
    
    @app.route('/debug/session')
    def debug_session():
        """
        Debug route to check session info
        """
        if 'user_id' in session:
            return {
                'logged_in': True,
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role'),
                'full_name': session.get('full_name'),
                'email': session.get('email')
            }
        return {'logged_in': False, 'message': 'No active session'}
    
    @app.route('/debug/users')
    def debug_users():
        """
        Debug route to list all users
        """
        try:
            users = User.query.all()
            result = []
            for user in users:
                result.append({
                    'id': user.user_id,
                    'username': user.username,
                    'role': user.role,
                    'full_name': user.full_name,
                    'email': user.email,
                    'hash_prefix': user.password_hash[:30] if user.password_hash else 'None'
                })
            return {'users': result, 'count': len(result)}
        except Exception as e:
            return {'error': str(e)}
    
    # ==================== DATABASE TEST ROUTES ====================
    
    @app.route('/test-db')
    def test_db():
        """
        Test database connection
        """
        try:
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            return {
                'status': 'success',
                'message': '✅ Database connected successfully!',
                'result': list(result)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'❌ Database connection failed: {str(e)}'
            }
    
    @app.route('/tables')
    def show_tables():
        """
        Show all tables in database
        """
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            html = "<h3>📊 Database Tables:</h3><ul>"
            for table in tables:
                html += f'<li>{table}</li>'
            html += f"</ul><p>Total: {len(tables)} tables</p>"
            return html
        except Exception as e:
            return f"Error: {str(e)}"
    
    @app.route('/test-model')
    def test_model():
        """
        Test User model
        """
        try:
            count = User.query.count()
            return f"✅ Model User loaded successfully!<br>Total users: {count}"
        except Exception as e:
            return f"❌ Model error: {str(e)}"
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def page_not_found(e):
        """
        Handle 404 errors
        """
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """
        Handle 500 errors
        """
        return render_template('errors/500.html'), 500
    
    # ==================== REGISTER BLUEPRINTS ====================
    try:
        # Import blueprints - KẾT HỢP CẢ HAI
        from routes.auth import auth_bp  # TỪ PHIÊN BẢN ĐẦU TIÊN
        from routes.student import student_bp
        from routes.admin import admin_bp
        
        # Đăng ký các blueprint
        app.register_blueprint(auth_bp)   # TỪ PHIÊN BẢN ĐẦU TIÊN
        app.register_blueprint(student_bp)
        app.register_blueprint(admin_bp)
        print("✅ Blueprints registered successfully")
        
    except ImportError as e:
        print(f"⚠️ Blueprint import error: {e}")
    
    return app


# ==================== APPLICATION ENTRY POINT ====================
if __name__ == '__main__':
    # Print configuration for debugging
    try:
        Config.print_config()
    except:
        print("⚠️ Could not print config")
    
    # Create application
    app = create_app()
    
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables verified/created")
            
            # Check if we have any users
            user_count = User.query.count()
            print(f"👥 Total users in database: {user_count}")
            
            if user_count == 0:
                print("⚠️ No users found in database!")
                # GIỮ CẢ HAI THÔNG BÁO
                print("⚠️ Run: python Backend/create_sample_data.py to create sample users")
                print("⚠️ OR Run: python Backend/fix_password_hash.py to create sample users")
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    # Start server - KẾT HỢP THÔNG BÁO TỪ CẢ HAI
    print("\n" + "=" * 50)
    print("🚀 Course Registration System")
    print("=" * 50)
    print(f"📡 Server URL: http://localhost:5000")
    print(f"🔐 Login URL: http://localhost:5000/login")
    print(f"📚 Student Management: http://localhost:5000/admin/students")  # TỪ PHIÊN BẢN 2
    print(f"👨‍💼 Admin: admin001 / password123")
    print(f"👨‍🎓 Student: student001 / password123")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )