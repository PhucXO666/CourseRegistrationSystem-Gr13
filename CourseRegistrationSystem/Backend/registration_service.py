from models import db
from models import (
    Student, ClassSection, Registration, 
    RegistrationPeriod, Course, Prerequisite
)
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

class RegistrationService:
    
    @staticmethod
    def check_registration_period(semester):
        """
        Kiểm tra xem hiện tại có trong thời gian đăng ký không
        
        Args:
            semester: Học kỳ cần kiểm tra
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            now = datetime.now()
            
            # Tìm đợt đăng ký đang hoạt động cho học kỳ
            active_period = RegistrationPeriod.query.filter(
                RegistrationPeriod.semester == semester,
                RegistrationPeriod.is_active == True,
                RegistrationPeriod.start_time <= now,
                RegistrationPeriod.end_time >= now
            ).first()
            
            if not active_period:
                return False, f"Không trong thời gian đăng ký cho học kỳ {semester}"
            
            return True, "Thời gian đăng ký hợp lệ"
            
        except Exception as e:
            return False, f"Lỗi khi kiểm tra thời gian đăng ký: {str(e)}"
    
    @staticmethod
    def check_prerequisite(student_id, class_section):
        """
        Kiểm tra điều kiện tiên quyết của sinh viên cho một lớp học
        
        Args:
            student_id: Mã sinh viên
            class_section: Đối tượng ClassSection
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Lấy danh sách môn học tiên quyết
            prerequisites = Prerequisite.query.filter_by(
                course_code=class_section.course_code
            ).all()
            
            if not prerequisites:
                return True, "Không có điều kiện tiên quyết"
            
            # Lấy danh sách các môn sinh viên đã hoàn thành (đã đăng ký và lớp đã kết thúc)
            completed_courses = db.session.query(
                Course.course_code
            ).join(ClassSection, Course.course_code == ClassSection.course_code)\
             .join(Registration, ClassSection.class_id == Registration.class_id)\
             .filter(
                Registration.student_id == student_id,
                Registration.status == 'registered',
                ClassSection.end_date < datetime.now().date()
            ).all()
            
            completed_course_codes = {course.course_code for course in completed_courses}
            
            # Kiểm tra từng điều kiện tiên quyết
            for prereq in prerequisites:
                if prereq.prerequisite_code not in completed_course_codes:
                    # Kiểm tra xem sinh viên đang đăng ký môn tiên quyết không
                    current_registration = Registration.query.join(ClassSection).filter(
                        Registration.student_id == student_id,
                        Registration.status == 'registered',
                        ClassSection.course_code == prereq.prerequisite_code,
                        ClassSection.semester == class_section.semester
                    ).first()
                    
                    if not current_registration:
                        prereq_course = Course.query.get(prereq.prerequisite_code)
                        course_name = prereq_course.course_name if prereq_course else prereq.prerequisite_code
                        return False, f"Chưa hoàn thành môn tiên quyết: {course_name}"
            
            return True, "Đạt điều kiện tiên quyết"
            
        except Exception as e:
            return False, f"Lỗi khi kiểm tra điều kiện tiên quyết: {str(e)}"
    
    @staticmethod
    def check_schedule_conflict(class_sections):
        """
        Kiểm tra xung đột lịch học giữa các lớp
        
        Args:
            class_sections: Danh sách đối tượng ClassSection
            
        Returns:
            tuple: (is_valid, error_message, conflicting_pairs)
        """
        try:
            if len(class_sections) < 2:
                return True, "Không có xung đột lịch học", []
            
            # Parse schedule_info để kiểm tra xung đột
            # Đơn giản hóa: chỉ kiểm tra nếu schedule_info giống nhau
            schedule_groups = {}
            for cls in class_sections:
                if cls.schedule_info:
                    if cls.schedule_info not in schedule_groups:
                        schedule_groups[cls.schedule_info] = []
                    schedule_groups[cls.schedule_info].append(cls)
            
            conflicting_pairs = []
            for schedule, classes in schedule_groups.items():
                if len(classes) > 1:
                    for i in range(len(classes)):
                        for j in range(i + 1, len(classes)):
                            conflicting_pairs.append((classes[i], classes[j]))
            
            if conflicting_pairs:
                conflict_info = []
                for cls1, cls2 in conflicting_pairs:
                    conflict_info.append(f"{cls1.class_code} - {cls2.class_code}")
                return False, f"Xung đột lịch học: {'; '.join(conflict_info)}", conflicting_pairs
            
            return True, "Không có xung đột lịch học", []
            
        except Exception as e:
            return False, f"Lỗi khi kiểm tra xung đột lịch học: {str(e)}", []
    
    @staticmethod
    def check_credit_limit(student_id, class_sections, semester, max_credits=20):
        """
        Kiểm tra giới hạn số tín chỉ
        
        Args:
            student_id: Mã sinh viên
            class_sections: Danh sách đối tượng ClassSection
            semester: Học kỳ
            max_credits: Số tín chỉ tối đa (mặc định 20)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Tính tổng tín chỉ của các lớp muốn đăng ký
            new_credits = sum(
                cls.course.credits for cls in class_sections if cls.course
            )
            
            # Lấy tổng tín chỉ đã đăng ký trong học kỳ này
            registered_credits = db.session.query(
                db.func.sum(Course.credits)
            ).join(ClassSection, Course.course_code == ClassSection.course_code)\
             .join(Registration, ClassSection.class_id == Registration.class_id)\
             .filter(
                Registration.student_id == student_id,
                Registration.status == 'registered',
                ClassSection.semester == semester
            ).scalar() or 0
            
            total_credits = registered_credits + new_credits
            
            if total_credits > max_credits:
                return False, (
                    f"Vượt quá giới hạn tín chỉ: "
                    f"Đã có {registered_credits} tín chỉ, "
                    f"đăng ký thêm {new_credits} tín chỉ, "
                    f"tổng {total_credits}/{max_credits} tín chỉ"
                )
            
            return True, f"Số tín chỉ hợp lệ: {total_credits}/{max_credits}"
            
        except Exception as e:
            return False, f"Lỗi khi kiểm tra giới hạn tín chỉ: {str(e)}"
    
    @staticmethod
    def check_class_capacity(class_sections):
        """
        Kiểm tra sĩ số các lớp học
        
        Args:
            class_sections: Danh sách đối tượng ClassSection
            
        Returns:
            tuple: (is_valid, error_message, full_classes)
        """
        try:
            full_classes = []
            canceled_classes = []
            
            for cls in class_sections:
                if cls.status == 'Canceled':
                    canceled_classes.append(cls.class_code)
                elif cls.current_enrollment >= cls.max_capacity:
                    full_classes.append(cls.class_code)
            
            if canceled_classes:
                return False, f"Các lớp đã bị hủy: {', '.join(canceled_classes)}", []
            
            if full_classes:
                return False, f"Các lớp đã đầy: {', '.join(full_classes)}", full_classes
            
            return True, "Tất cả lớp đều còn chỗ", []
            
        except Exception as e:
            return False, f"Lỗi khi kiểm tra sĩ số lớp: {str(e)}", []
    
    @staticmethod
    def confirm_registration(student_id, class_ids):
        """
        Xác nhận đăng ký học phần với transaction
        
        Args:
            student_id: Mã sinh viên
            class_ids: Danh sách ID lớp học
            
        Returns:
            dict: Kết quả đăng ký
        """
        # Bắt đầu transaction
        db.session.begin()
        try:
            # 1. Kiểm tra sinh viên tồn tại
            student = Student.query.get(student_id)
            if not student:
                db.session.rollback()
                return {
                    'success': False,
                    'error': 'Sinh viên không tồn tại'
                }
            
            # 2. Lấy thông tin các lớp học
            class_sections = ClassSection.query.filter(
                ClassSection.class_id.in_(class_ids)
            ).all()
            
            if len(class_sections) != len(class_ids):
                found_ids = [cls.class_id for cls in class_sections]
                missing_ids = [cid for cid in class_ids if cid not in found_ids]
                db.session.rollback()
                return {
                    'success': False,
                    'error': f'Không tìm thấy lớp học: {missing_ids}'
                }
            
            # 3. Kiểm tra học kỳ (tất cả lớp phải cùng học kỳ)
            semesters = {cls.semester for cls in class_sections}
            if len(semesters) != 1:
                db.session.rollback()
                return {
                    'success': False,
                    'error': f'Các lớp thuộc nhiều học kỳ: {semesters}'
                }
            
            semester = list(semesters)[0]
            
            # 4. Kiểm tra thời gian đăng ký
            valid, error = RegistrationService.check_registration_period(semester)
            if not valid:
                db.session.rollback()
                return {
                    'success': False,
                    'error': error
                }
            
            # 5. Kiểm tra sĩ số lớp
            valid, error, full_classes = RegistrationService.check_class_capacity(class_sections)
            if not valid:
                db.session.rollback()
                return {
                    'success': False,
                    'error': error
                }
            
            # 6. Kiểm tra xung đột lịch học
            valid, error, conflicts = RegistrationService.check_schedule_conflict(class_sections)
            if not valid:
                db.session.rollback()
                return {
                    'success': False,
                    'error': error
                }
            
            # 7. Kiểm tra giới hạn tín chỉ
            valid, error = RegistrationService.check_credit_limit(
                student_id, class_sections, semester
            )
            if not valid:
                db.session.rollback()
                return {
                    'success': False,
                    'error': error
                }
            
            # 8. Kiểm tra điều kiện tiên quyết cho từng lớp
            for class_section in class_sections:
                valid, error = RegistrationService.check_prerequisite(student_id, class_section)
                if not valid:
                    db.session.rollback()
                    return {
                        'success': False,
                        'error': f"Lớp {class_section.class_code}: {error}"
                    }
            
            # 9. Kiểm tra đã đăng ký lớp này chưa
            existing_registrations = Registration.query.filter(
                Registration.student_id == student_id,
                Registration.class_id.in_(class_ids),
                Registration.status == 'registered'
            ).all()
            
            if existing_registrations:
                existing_classes = [
                    ClassSection.query.get(reg.class_id).class_code 
                    for reg in existing_registrations
                ]
                db.session.rollback()
                return {
                    'success': False,
                    'error': f'Đã đăng ký các lớp: {", ".join(existing_classes)}'
                }
            
            # 10. Tạo các bản ghi đăng ký
            registrations = []
            for class_section in class_sections:
                registration = Registration(
                    student_id=student_id,
                    class_id=class_section.class_id,
                    registration_time=datetime.now(),
                    status='registered'
                )
                db.session.add(registration)
                registrations.append(registration)
                
                # Cập nhật số lượng đăng ký của lớp
                class_section.current_enrollment += 1
            
            # 11. Commit transaction
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Đăng ký thành công {len(registrations)} lớp học',
                'registrations': [
                    {
                        'registration_id': reg.registration_id,
                        'class_id': reg.class_id,
                        'class_code': next(
                            cls.class_code for cls in class_sections 
                            if cls.class_id == reg.class_id
                        ),
                        'course_code': next(
                            cls.course_code for cls in class_sections 
                            if cls.class_id == reg.class_id
                        ),
                        'registration_time': reg.registration_time.isoformat()
                    }
                    for reg in registrations
                ]
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Lỗi database: {str(e)}'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Lỗi hệ thống: {str(e)}'
            }