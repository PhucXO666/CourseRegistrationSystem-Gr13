// ========== BIẾN TOÀN CỤC ==========
let tentativeClasses = [];

// ========== HÀM TÌM KIẾM MÔN HỌC ==========
function searchCourses() {
    const keyword = document.getElementById('searchInput').value;
    console.log('🔍 Tìm kiếm từ khóa:', keyword);
    
    // TODO: Thay bằng API thật khi Thảo làm xong
    // const response = await fetch(`/api/courses?q=${keyword}`);
    // const courses = await response.json();
    
    // Dữ liệu giả để TEST
    const mockData = [
        {
            id: 'CS101-01',
            code: 'CS101',
            name: 'Nhập môn lập trình',
            credits: 3,
            instructor: 'Nguyễn Văn A',
            schedule: 'T2, tiết 1-3',
            room: 'A1.101',
            available: 15,
            capacity: 60
        },
        {
            id: 'MATH201-01',
            code: 'MATH201',
            name: 'Toán rời rạc',
            credits: 3,
            instructor: 'Trần Thị B',
            schedule: 'T3, tiết 4-6',
            room: 'B2.201',
            available: 5,
            capacity: 50
        },
        {
            id: 'ENG101-01',
            code: 'ENG101',
            name: 'Anh văn 1',
            credits: 2,
            instructor: 'Lê Thị C',
            schedule: 'T4, tiết 7-8',
            room: 'C3.301',
            available: 20,
            capacity: 40
        }
    ];
    
    // Lọc theo từ khóa (giả lập)
    const filtered = mockData.filter(course => 
        course.code.toLowerCase().includes(keyword.toLowerCase()) ||
        course.name.toLowerCase().includes(keyword.toLowerCase())
    );
    
    renderCourses(filtered.length > 0 ? filtered : mockData);
}

// ========== HIỂN THỊ DANH SÁCH MÔN ==========
function renderCourses(courses) {
    const container = document.getElementById('courseResults');
    if (!container) {
        console.error('❌ Không tìm thấy element #courseResults');
        return;
    }
    
    container.innerHTML = '';
    
    if (courses.length === 0) {
        container.innerHTML = '<p class="no-results">Không tìm thấy môn học nào.</p>';
        return;
    }
    
    courses.forEach(course => {
        const div = document.createElement('div');
        div.className = 'course-card';
        div.innerHTML = `
            <h3>${course.code} - ${course.name} (${course.credits} tín chỉ)</h3>
            <p><strong>Giảng viên:</strong> ${course.instructor}</p>
            <p><strong>Lịch học:</strong> ${course.schedule}</p>
            <p><strong>Phòng:</strong> ${course.room}</p>
            <p><strong>Chỗ còn lại:</strong> ${course.available}/${course.capacity}</p>
            <button onclick="addToTentative('${course.id}')" class="btn-select">
                ✅ Chọn lớp
            </button>
        `;
        container.appendChild(div);
    });
    
    console.log(`✅ Đã hiển thị ${courses.length} môn học`);
}

// ========== THÊM VÀO DANH SÁCH TẠM ==========
async function addToTentative(classId) {
    console.log('➕ Thêm lớp:', classId);
    
    // TODO: Thay bằng API thật
    // const response = await fetch('/api/tentative/add', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ class_id: classId })
    // });
    
    // Giả lập thành công
    alert(`✅ Đã thêm lớp ${classId} vào danh sách tạm thời`);
    loadTentativeList();
}

// ========== TẢI DANH SÁCH TẠM ==========
async function loadTentativeList() {
    console.log('📋 Đang tải danh sách tạm thời...');
    
    // TODO: Thay bằng API thật
    // const response = await fetch('/api/tentative/list');
    // tentativeClasses = await response.json();
    
    // Dữ liệu giả
    tentativeClasses = [
        {
            id: 'CS101-01',
            code: 'CS101',
            name: 'Nhập môn lập trình',
            schedule: 'T2, tiết 1-3',
            hasConflict: false
        }
    ];
    
    renderTentativeList();
}

// ========== HIỂN THỊ DANH SÁCH TẠM ==========
function renderTentativeList() {
    const container = document.getElementById('tentativeList');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (tentativeClasses.length === 0) {
        container.innerHTML = '<p class="empty-list">Chưa có lớp nào trong danh sách tạm thời.</p>';
        return;
    }
    
    tentativeClasses.forEach(cls => {
        const div = document.createElement('div');
        div.className = 'tentative-item';
        if (cls.hasConflict) {
            div.classList.add('conflict');
        }
        div.innerHTML = `
            <div class="tentative-info">
                <strong>${cls.code}</strong> - ${cls.name}
                <br><small>${cls.schedule}</small>
            </div>
            <button onclick="removeFromTentative('${cls.id}')" class="btn-remove">
                ❌ Xóa
            </button>
        `;
        container.appendChild(div);
    });
}

// ========== XÓA KHỎI DANH SÁCH TẠM ==========
async function removeFromTentative(classId) {
    console.log('➖ Xóa lớp:', classId);
    
    // TODO: Thay bằng API thật
    // const response = await fetch('/api/tentative/remove', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ class_id: classId })
    // });
    
    // Giả lập
    tentativeClasses = tentativeClasses.filter(cls => cls.id !== classId);
    renderTentativeList();
    alert(`✅ Đã xóa lớp khỏi danh sách tạm thời`);
}

// ========== XÁC NHẬN ĐĂNG KÝ ==========
async function confirmRegistration() {
    console.log('📝 Đang xác nhận đăng ký...');
    
    if (tentativeClasses.length === 0) {
        alert('❌ Vui lòng chọn ít nhất một lớp học!');
        return;
    }
    
    // TODO: Thay bằng API thật
    // const response = await fetch('/api/register/confirm', {
    //     method: 'POST'
    // });
    // const result = await response.json();
    
    // Giả lập
    const result = { success: true, message: 'Đăng ký thành công!' };
    
    if (result.success) {
        alert('🎉 Đăng ký thành công!');
        // window.location.href = '/student/results';
    } else {
        alert('❌ Đăng ký thất bại: ' + result.message);
    }
}

// ========== KHỞI TẠO KHI TRANG LOAD ==========
window.onload = function() {
    console.log('🚀 Trang course_search đã load xong');
    loadTentativeList();
    searchCourses(); // Load tất cả môn học ban đầu
};

// ========== HÀM KIỂM TRA CONFLICT ==========
function checkTimeConflicts() {
    // Logic kiểm tra trùng giờ sẽ được Thảo implement
    console.log('⏰ Đang kiểm tra xung đột thời gian...');
    return false; // Giả lập không có conflict
}