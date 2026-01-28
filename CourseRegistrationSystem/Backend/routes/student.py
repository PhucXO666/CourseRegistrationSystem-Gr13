# routes/student.py
from flask import Blueprint, render_template, redirect, url_for
from extensions import db
from datetime import datetime
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models SAU KHI đã có db
student_bp = Blueprint('student', __name__, url_prefix='/student')

# ========== HELPER FUNCTIONS ==========
def get_current_student():
    """Lấy sinh viên hiện tại (tạm thời lấy đầu tiên)"""
    from models import Student
    student = Student.query.first()
    if not student:
        logger.warning("Không tìm thấy sinh viên")
    return student

def get_student_user(student):
    """Lấy thông tin user của sinh viên"""
    from models import User
    if not student:
        return None
    return User.query.get(student.user_id)

def calculate_tuition_details(registrations):
    """Tính toán chi tiết học phí từ danh sách đăng ký"""
    from models import ClassSection, Course
    
    if not registrations:
        return [], 0, 0
    
    registration_details = []
    total_credits = 0
    total_tuition = 0
    credit_price = 500000  # 500,000 VND/tín chỉ
    
    for reg in registrations:
        class_section = ClassSection.query.get(reg.class_id)
        if class_section:
            course = Course.query.filter_by(course_code=class_section.course_code).first()
            
            if course:
                # Lấy số tín chỉ
                credits = getattr(course, 'credits', 3)
                if not isinstance(credits, (int, float)):
                    credits = 3
                    logger.warning(f"Credits không hợp lệ cho course {course.course_code}, đặt mặc định là 3")
                
                total_credits += credits
                tuition = credits * credit_price
                total_tuition += tuition
                
                # Tạo thông tin chi tiết
                registration_details.append({
                    'course': course,
                    'class_section': class_section,
                    'registration': reg,
                    'credits': credits,
                    'tuition': tuition
                })
    
    # Đảm bảo giá trị hợp lệ
    total_credits = float(total_credits) if isinstance(total_credits, (int, float)) else 0.0
    total_tuition = float(total_tuition) if isinstance(total_tuition, (int, float)) else 0.0
    
    return registration_details, total_credits, total_tuition

# ========== ROUTES ==========
@student_bp.route('/dashboard')
def dashboard():
    """Trang dashboard sinh viên"""
    try:
        from models import Student, ClassSection, Course, Registration, RegistrationPeriod, User
        
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        # Lấy kỳ đăng ký hiện tại
        current_period = RegistrationPeriod.query.filter(
            RegistrationPeriod.start_time <= datetime.now(),
            RegistrationPeriod.end_time >= datetime.now()
        ).first()
        
        # Lấy các lớp học đang mở đăng ký
        if current_period:
            available_classes = ClassSection.query.filter(
                ClassSection.semester == current_period.semester
            ).all()
        else:
            available_classes = []
            logger.info("Không có kỳ đăng ký hiện tại")
        
        # Lấy các lớp sinh viên đã đăng ký
        registrations = Registration.query.filter_by(student_id=student.student_id).all()
        registered_class_ids = [reg.class_id for reg in registrations]
        registered_classes = ClassSection.query.filter(ClassSection.class_id.in_(registered_class_ids)).all() if registered_class_ids else []
        
        # Tính total credits
        total_credits = 0
        for cls in registered_classes:
            course = Course.query.filter_by(course_code=cls.course_code).first()
            if course and hasattr(course, 'credits'):
                credits = course.credits
                if isinstance(credits, (int, float)):
                    total_credits += credits
                else:
                    logger.warning(f"Credits không hợp lệ: {credits} cho course {course.course_code}")
        
        # Tạo stats data
        stats = {
            'registered_courses': len(registered_classes),
            'total_credits': total_credits,
            'tentative_count': 0,
            'estimated_tuition': len(registered_classes) * 1500,
            'gpa': 3.5
        }
        
        return render_template(
            'student/dashboard.html',
            student=student,
            user=user,
            available_classes=available_classes,
            registered_classes=registered_classes,
            current_period=current_period,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Lỗi trong dashboard: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/schedule')
def view_schedule():
    """Trang xem thời khóa biểu"""
    try:
        from models import Student, ClassSection, Course, Registration, User
        
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        # Lấy các lớp đã đăng ký
        registrations = Registration.query.filter_by(student_id=student.student_id).all()
        
        # Lấy thông tin chi tiết các lớp
        schedule_data = []
        for reg in registrations:
            class_section = ClassSection.query.get(reg.class_id)
            if class_section:
                course = Course.query.filter_by(course_code=class_section.course_code).first()
                
                if course:
                    # Lấy thông tin thời gian
                    day_of_week = getattr(class_section, 'day_of_week', 'Thứ 2')
                    start_period = getattr(class_section, 'start_period', 
                                         getattr(class_section, 'start_time', 1))
                    end_period = getattr(class_section, 'end_period',
                                       getattr(class_section, 'end_time', 3))
                    
                    schedule_data.append({
                        'class': {
                            'obj': class_section,
                            'day_of_week': day_of_week,
                            'start_period': start_period,
                            'end_period': end_period,
                            'room': getattr(class_section, 'room', 'Chưa xác định'),
                            'instructor': getattr(class_section, 'instructor', 'Chưa xác định'),
                            'class_code': getattr(class_section, 'class_code', '')
                        },
                        'course': course,
                        'registration': reg
                    })
        
        return render_template(
            'student/schedule.html',
            student=student,
            user=user,
            schedule=schedule_data
        )
    except Exception as e:
        logger.error(f"Lỗi trong view_schedule: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/courses')
def view_courses():
    """Trang xem danh sách học phần"""
    try:
        from models import Student, User, Course, ClassSection
        
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        # Lấy tất cả học phần
        courses = Course.query.all()
        
        # Tạo danh sách chi tiết
        course_details = []
        for course in courses:
            # Lấy các lớp học cho mỗi học phần
            classes = ClassSection.query.filter_by(course_code=course.course_code).all()
            course_details.append({
                'course': course,
                'classes': classes,
                'class_count': len(classes)
            })
        
        return render_template(
            'student/course_search.html',
            student=student,
            user=user,
            course_details=course_details,
            page_title="Danh sách Học phần"
        )
    except Exception as e:
        logger.error(f"Lỗi trong view_courses: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/search-courses')
def search_courses_page():
    """Trang tìm kiếm học phần"""
    try:
        student = get_current_student()
        user = get_student_user(student) if student else None
        
        return render_template(
            'student/course_search.html',
            student=student,
            user=user
        )
    except Exception as e:
        logger.error(f"Lỗi trong search_courses_page: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/tentative-list')
def tentative_list_page():
    """Trang danh sách tạm"""
    try:
        student = get_current_student()
        user = get_student_user(student) if student else None
        
        return render_template(
            'student/tentative_list.html',
            student=student,
            user=user
        )
    except Exception as e:
        logger.error(f"Lỗi trong tentative_list_page: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/confirm-registration')
def confirm_registration_page():
    """Trang xác nhận đăng ký"""
    # Chuyển hướng đến trang registration_results để tránh trùng lặp code
    return redirect(url_for('student.registration_results'))

@student_bp.route('/registration-results')
def registration_results():
    """Trang kết quả đăng ký - ĐƯỢC SỬ DỤNG CHO CẢ CONFIRM-REGISTRATION"""
    try:
        from models import Student, User, Registration
        
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        # Lấy danh sách đăng ký
        registrations = Registration.query.filter_by(student_id=student.student_id).all()
        
        # Tính toán chi tiết học phí
        registration_details, total_credits, total_tuition = calculate_tuition_details(registrations)
        
        # Cập nhật thông tin sinh viên cho template
        student.name = getattr(student, 'full_name', f"Sinh viên {getattr(student, 'student_id', 'N/A')}")
        student.min_credits = getattr(student, 'min_credits', 12)
        student.max_credits = getattr(student, 'max_credits', 22)
        
        logger.info(f"Hiển thị registration results: {len(registration_details)} môn, {total_credits} tín chỉ, {total_tuition} VND")
        
        return render_template(
            'student/registration_results.html',
            student=student,
            user=user,
            registrations=registration_details,
            total_credits=total_credits,
            total_tuition=total_tuition,
            credit_price=500000
        )
    except Exception as e:
        logger.error(f"Lỗi trong registration_results: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

# ========== ADDITIONAL ROUTES ==========
@student_bp.route('/profile')
def view_profile():
    """Trang xem thông tin cá nhân"""
    try:
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        return render_template(
            'student/profile.html',
            student=student,
            user=user
        )
    except Exception as e:
        logger.error(f"Lỗi trong view_profile: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

@student_bp.route('/grades')
def view_grades():
    """Trang xem điểm"""
    try:
        student = get_current_student()
        if not student:
            return "Không tìm thấy sinh viên", 404
        
        user = get_student_user(student)
        
        # Lấy thông tin điểm (tạm thời dùng dữ liệu mẫu)
        sample_grades = [
            {'course': 'CS101', 'course_name': 'Nhập môn lập trình', 'grade': 'A', 'credits': 3},
            {'course': 'MATH101', 'course_name': 'Toán cao cấp', 'grade': 'B+', 'credits': 4},
            {'course': 'ENG101', 'course_name': 'Tiếng Anh chuyên ngành', 'grade': 'A-', 'credits': 2},
        ]
        
        return render_template(
            'student/grades.html',
            student=student,
            user=user,
            grades=sample_grades,
            gpa=3.5
        )
    except Exception as e:
        logger.error(f"Lỗi trong view_grades: {str(e)}")
        return f"Lỗi server: {str(e)}", 500

# ========== ERROR HANDLER ==========
@student_bp.errorhandler(404)
def page_not_found(e):
    return render_template('student/404.html'), 404

@student_bp.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Lỗi 500: {str(e)}")
    return render_template('student/500.html'), 500
