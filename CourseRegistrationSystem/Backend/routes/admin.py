# routes/admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, send_file, url_for, flash
from requests import session
from extensions import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

import pandas as pd
from io import BytesIO

@admin_bp.route('/download-template')
def download_template():
    """Tải template Excel mẫu"""
    # Tạo DataFrame mẫu
    sample_data = {
        'student_id': ['SV001', 'SV002', 'SV003'],
        'full_name': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'],
        'email': ['sv001@school.edu.vn', 'sv002@school.edu.vn', 'sv003@school.edu.vn'],
        'enrollment_year': [2023, 2023, 2023],
        'date_of_birth': ['2002-01-15', '2002-03-20', '2002-05-10'],
        'major': ['Công nghệ thông tin', 'Kinh tế', 'Kỹ thuật']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Tạo file Excel trong memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Students', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='template_sinh_vien.xlsx'
    )

@admin_bp.route('/dashboard')
def admin_dashboard():
    # Import trong hàm
    from models import Course, ClassSection, Student, Registration, RegistrationPeriod
    
    # Thống kê
    total_courses = Course.query.count()
    total_classes = ClassSection.query.count()
    total_students = Student.query.count()
    total_registrations = Registration.query.count()
    total_periods = RegistrationPeriod.query.count()
    
    # Lấy số lớp đang mở
    open_classes = ClassSection.query.filter_by(status='Open').count()
    
    # Lấy số lớp sắp đầy (từ 80% capacity trở lên)
    all_classes = ClassSection.query.all()
    nearly_full_classes = sum(1 for c in all_classes 
                              if c.current_enrollment >= (c.max_capacity * 0.8))
    
    # Lấy số kỳ đăng ký hoạt động
    active_periods = RegistrationPeriod.query.filter_by(is_active=True).count()
    
    # Lấy lớp học gần đây
    recent_classes = ClassSection.query.order_by(ClassSection.class_id.desc()).limit(5).all()
    
    # Lấy kỳ đăng ký hiện tại
    current_period = RegistrationPeriod.query.filter(
        RegistrationPeriod.start_time <= datetime.now(),
        RegistrationPeriod.end_time >= datetime.now()
    ).first()
    
    return render_template(
        'admin/dashboard.html',
        total_courses=total_courses,
        total_classes=total_classes,
        total_students=total_students,
        total_registrations=total_registrations,
        total_periods=total_periods,
        open_classes=open_classes,
        nearly_full_classes=nearly_full_classes,
        active_periods=active_periods,
        recent_classes=recent_classes,
        current_period=current_period
    )

@admin_bp.route('/courses')
def manage_courses():
    from models import Course
    courses = Course.query.order_by(Course.course_code).all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/classes')
def manage_classes():
    from models import ClassSection, Course
    classes = ClassSection.query.all()
    
    # Thêm thông tin course cho mỗi lớp
    class_details = []
    for class_section in classes:
        course = Course.query.get(class_section.course_code)
        class_details.append({
            'class_section': class_section,
            'course': course
        })
    
    return render_template('admin/classes.html', class_details=class_details)

@admin_bp.route('/registration-periods')
def manage_registration_periods():
    from models import RegistrationPeriod
    periods = RegistrationPeriod.query.order_by(RegistrationPeriod.start_time.desc()).all()
    return render_template('admin/registration_periods.html', periods=periods)

@admin_bp.route('/reports')
def view_reports():
    """Xem báo cáo"""
    from models import Course, ClassSection, Student, Registration, RegistrationPeriod
    
    # Thống kê tổng hợp
    total_courses = Course.query.count()
    total_classes = ClassSection.query.count()
    total_students = Student.query.count()
    total_registrations = Registration.query.count()
    
    # Thống kê theo course
    courses_stats = []
    courses = Course.query.all()
    for course in courses[:10]:  # Top 10 courses
        course_registrations = Registration.query.join(
            ClassSection, Registration.class_id == ClassSection.class_id
        ).filter(ClassSection.course_code == course.course_code).count()
        
        courses_stats.append({
            'course': course,
            'registrations': course_registrations
        })
    
    return render_template(
        'admin/reports.html',
        total_courses=total_courses,
        total_classes=total_classes,
        total_students=total_students,
        total_registrations=total_registrations,
        courses_stats=courses_stats
    )

# ==================== API ROUTES ====================

@admin_bp.route('/api/courses', methods=['POST'])
def add_course():
    """Thêm course mới"""
    from models import Course
    
    try:
        data = request.get_json()
        
        # Kiểm tra dữ liệu
        if not data.get('course_code') or not data.get('course_name') or not data.get('credits'):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400
        
        # Kiểm tra course code đã tồn tại
        existing = Course.query.get(data['course_code'])
        if existing:
            return jsonify({'success': False, 'message': 'Mã học phần đã tồn tại'}), 400
        
        # Tạo course mới
        new_course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            credits=int(data['credits']),
            description=data.get('description', ''),
            is_active=True
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Thêm học phần thành công',
            'course': {
                'code': new_course.course_code,
                'name': new_course.course_name,
                'credits': new_course.credits
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/courses/<course_code>', methods=['PUT'])
def update_course(course_code):
    """Cập nhật course"""
    from models import Course
    
    try:
        course = Course.query.get(course_code)
        if not course:
            return jsonify({'success': False, 'message': 'Không tìm thấy học phần'}), 404
        
        data = request.get_json()
        
        # Cập nhật thông tin
        course.course_name = data.get('course_name', course.course_name)
        course.credits = int(data.get('credits', course.credits))
        course.description = data.get('description', course.description)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Cập nhật học phần thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/courses/<course_code>', methods=['DELETE'])
def delete_course(course_code):
    """Xóa course"""
    from models import Course
    
    try:
        course = Course.query.get(course_code)
        if not course:
            return jsonify({'success': False, 'message': 'Không tìm thấy học phần'}), 404
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Xóa học phần thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/courses-list', methods=['GET'])
def get_courses_list():
    """Lấy danh sách courses cho dropdown"""
    from models import Course
    
    courses = Course.query.filter_by(is_active=True).all()
    return jsonify({
        'courses': [{'code': c.course_code, 'name': c.course_name} for c in courses]
    }), 200

@admin_bp.route('/api/classes', methods=['POST'])
def add_class():
    """Thêm class mới"""
    from models import ClassSection
    
    try:
        data = request.get_json()
        
        if not data.get('class_code') or not data.get('course_code'):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400
        
        new_class = ClassSection(
            class_code=data['class_code'],
            course_code=data['course_code'],
            semester=data.get('semester', 'Unknown'),
            max_capacity=int(data.get('max_capacity', 30)),
            current_enrollment=0,
            status='Open'
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Thêm lớp thành công'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    """Cập nhật class"""
    from models import ClassSection
    
    try:
        class_section = ClassSection.query.get(class_id)
        if not class_section:
            return jsonify({'success': False, 'message': 'Không tìm thấy lớp'}), 404
        
        data = request.get_json()
        
        class_section.class_code = data.get('class_code', class_section.class_code)
        class_section.semester = data.get('semester', class_section.semester)
        class_section.max_capacity = int(data.get('max_capacity', class_section.max_capacity))
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cập nhật lớp thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    """Xóa class"""
    from models import ClassSection
    
    try:
        class_section = ClassSection.query.get(class_id)
        if not class_section:
            return jsonify({'success': False, 'message': 'Không tìm thấy lớp'}), 404
        
        db.session.delete(class_section)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Xóa lớp thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/registration-periods', methods=['POST'])
def add_registration_period():
    """Thêm registration period mới"""
    from models import RegistrationPeriod
    
    try:
        data = request.get_json()
        
        if not data.get('period_name') or not data.get('semester'):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400
        
        new_period = RegistrationPeriod(
            period_name=data['period_name'],
            semester=data['semester'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            is_active=data.get('is_active', False)
        )
        
        db.session.add(new_period)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Thêm đợt đăng ký thành công'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/registration-periods/<int:period_id>', methods=['PUT'])
def update_registration_period(period_id):
    """Cập nhật registration period"""
    from models import RegistrationPeriod
    
    try:
        period = RegistrationPeriod.query.get(period_id)
        if not period:
            return jsonify({'success': False, 'message': 'Không tìm thấy đợt đăng ký'}), 404
        
        data = request.get_json()
        
        period.period_name = data.get('period_name', period.period_name)
        period.semester = data.get('semester', period.semester)
        if data.get('start_time'):
            period.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            period.end_time = datetime.fromisoformat(data['end_time'])
        period.is_active = data.get('is_active', period.is_active)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cập nhật đợt đăng ký thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/api/registration-periods/<int:period_id>', methods=['DELETE'])
def delete_registration_period(period_id):
    """Xóa registration period"""
    from models import RegistrationPeriod
    
    try:
        period = RegistrationPeriod.query.get(period_id)
        if not period:
            return jsonify({'success': False, 'message': 'Không tìm thấy đợt đăng ký'}), 404
        
        db.session.delete(period)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Xóa đợt đăng ký thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    
# routes/admin.py - Thêm vào cuối file admin.py

@admin_bp.route('/students')
def manage_students():
    """Trang quản lý sinh viên"""
    from models import Student, User
    students = Student.query.join(User).order_by(User.full_name).all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Thêm sinh viên thủ công"""
    from models import User, Student
    
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            student_id = request.form.get('student_id')
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            date_of_birth = request.form.get('date_of_birth')
            major = request.form.get('major')
            enrollment_year = request.form.get('enrollment_year')
            
            # Kiểm tra dữ liệu
            if not all([student_id, full_name, email, enrollment_year]):
                flash('Vui lòng nhập đầy đủ thông tin bắt buộc', 'error')
                return redirect(url_for('admin.add_student'))
            
            # Kiểm tra student_id đã tồn tại chưa
            if Student.query.get(student_id):
                flash('Mã sinh viên đã tồn tại', 'error')
                return redirect(url_for('admin.add_student'))
            
            # Tạo username từ student_id
            username = student_id
            
            # Kiểm tra username/email đã tồn tại chưa
            if User.query.filter_by(username=username).first():
                flash('Username đã tồn tại', 'error')
                return redirect(url_for('admin.add_student'))
            
            if User.query.filter_by(email=email).first():
                flash('Email đã tồn tại', 'error')
                return redirect(url_for('admin.add_student'))
            
            # Tạo user mới
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role='student'
            )
            # Mật khẩu mặc định
            new_user.set_password('password123')
            
            db.session.add(new_user)
            db.session.flush()  # Lấy user_id
            
            # Tạo sinh viên
            new_student = Student(
                student_id=student_id,
                user_id=new_user.user_id,
                date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
                major=major,
                enrollment_year=int(enrollment_year)
            )
            
            db.session.add(new_student)
            db.session.commit()
            
            flash('Thêm sinh viên thành công! Mật khẩu mặc định: password123', 'success')
            return redirect(url_for('admin.manage_students'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'error')
            return redirect(url_for('admin.add_student'))
    
    return render_template('admin/add_student.html')

@admin_bp.route('/students/import', methods=['GET', 'POST'])
def import_students():
    """Import sinh viên từ file Excel"""
    from models import User, Student
    import pandas as pd
    
    if request.method == 'POST':
        try:
            # Kiểm tra file
            if 'excel_file' not in request.files:
                flash('Vui lòng chọn file', 'error')
                return redirect(url_for('admin.import_students'))
            
            file = request.files['excel_file']
            if file.filename == '':
                flash('Vui lòng chọn file', 'error')
                return redirect(url_for('admin.import_students'))
            
            # Đọc file Excel
            df = pd.read_excel(file)
            
            # Kiểm tra các cột bắt buộc
            required_columns = ['student_id', 'full_name', 'email', 'enrollment_year']
            for col in required_columns:
                if col not in df.columns:
                    flash(f'Thiếu cột {col} trong file Excel', 'error')
                    return redirect(url_for('admin.import_students'))
            
            success_count = 0
            error_messages = []
            
            for index, row in df.iterrows():
                try:
                    student_id = str(row['student_id']).strip()
                    full_name = str(row['full_name']).strip()
                    email = str(row['email']).strip()
                    enrollment_year = int(row['enrollment_year'])
                    
                    # Kiểm tra student_id đã tồn tại
                    if Student.query.get(student_id):
                        error_messages.append(f'Dòng {index+2}: Mã sinh viên {student_id} đã tồn tại')
                        continue
                    
                    # Tạo username từ student_id
                    username = student_id
                    
                    # Kiểm tra username/email đã tồn tại
                    if User.query.filter_by(username=username).first():
                        error_messages.append(f'Dòng {index+2}: Username {username} đã tồn tại')
                        continue
                    
                    if User.query.filter_by(email=email).first():
                        error_messages.append(f'Dòng {index+2}: Email {email} đã tồn tại')
                        continue
                    
                    # Tạo user
                    new_user = User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        role='student'
                    )
                    # Mật khẩu mặc định
                    new_user.set_password('password123')
                    
                    db.session.add(new_user)
                    db.session.flush()
                    
                    # Xử lý các trường không bắt buộc
                    date_of_birth = None
                    if 'date_of_birth' in df.columns and pd.notna(row['date_of_birth']):
                        try:
                            if isinstance(row['date_of_birth'], str):
                                date_of_birth = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                            else:
                                date_of_birth = row['date_of_birth'].date()
                        except:
                            pass
                    
                    major = str(row['major']).strip() if 'major' in df.columns and pd.notna(row['major']) else ''
                    
                    # Tạo sinh viên
                    new_student = Student(
                        student_id=student_id,
                        user_id=new_user.user_id,
                        date_of_birth=date_of_birth,
                        major=major,
                        enrollment_year=enrollment_year
                    )
                    
                    db.session.add(new_student)
                    success_count += 1
                    
                except Exception as e:
                    error_messages.append(f'Dòng {index+2}: Lỗi - {str(e)}')
                    continue
            
            db.session.commit()
            
            if success_count > 0:
                flash(f'Import thành công {success_count} sinh viên. Mật khẩu mặc định: password123', 'success')
            
            if error_messages:
                flash(f'Có {len(error_messages)} lỗi xảy ra', 'warning')
                # Có thể lưu lỗi vào session để hiển thị chi tiết
                session['import_errors'] = error_messages[:10]  # Chỉ lưu 10 lỗi đầu
            
            return redirect(url_for('admin.manage_students'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi đọc file: {str(e)}', 'error')
            return redirect(url_for('admin.import_students'))
    
    return render_template('admin/import_students.html')

@admin_bp.route('/students/<student_id>/reset-password', methods=['POST'])
def reset_student_password(student_id):
    """Reset mật khẩu sinh viên"""
    from models import Student, User
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Không tìm thấy sinh viên'}), 404
        
        user = User.query.get(student.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Không tìm thấy tài khoản'}), 404
        
        # Reset về mật khẩu mặc định
        user.set_password('password123')
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Đã reset mật khẩu về mặc định: password123'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@admin_bp.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Xóa sinh viên"""
    from models import Student, User
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Không tìm thấy sinh viên'}), 404
        
        user = User.query.get(student.user_id)
        
        # Xóa sinh viên và user
        db.session.delete(student)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Xóa sinh viên thành công'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    # Thêm hàm này trong file routes/admin.py
def calculate_period_progress(period):
    """Tính % tiến độ của đợt đăng ký"""
    if not period:
        return 0
    
    now = datetime.now()
    total_duration = (period.end_time - period.start_time).total_seconds()
    elapsed = (now - period.start_time).total_seconds()
    
    if total_duration <= 0:
        return 0
    
    progress = (elapsed / total_duration) * 100
    return min(max(progress, 0), 100)

def get_time_ago(timestamp):
    """Chuyển timestamp thành text 'X giờ/phút/ngày trước'"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} ngày"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600} giờ"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60} phút"
    else:
        return "Vừa xong"

# Thêm vào context processor để dùng trong template
@admin_bp.context_processor
def utility_processor():
    return {
        'calculate_period_progress': calculate_period_progress,
        'get_time_ago': get_time_ago
    }