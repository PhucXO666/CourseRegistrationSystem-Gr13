# templates/helpers.py - Đặt trong thư mục templates hoặc root
from datetime import datetime

def get_period_time(period):
    """Get time for period"""
    times = {
        1: "7:00 - 7:50",
        2: "7:55 - 8:45",
        3: "8:50 - 9:40",
        4: "9:45 - 10:35",
        5: "10:40 - 11:30",
        6: "12:30 - 13:20",
        7: "13:25 - 14:15",
        8: "14:20 - 15:10",
        9: "15:15 - 16:05",
        10: "16:10 - 17:00",
        11: "17:05 - 17:55",
        12: "18:00 - 18:50"
    }
    return times.get(period, "N/A")

def get_course_color(course_code):
    """Get color based on course code"""
    color_map = {
        'MATH': '#4e73df',    # Blue
        'PHYS': '#4e73df',    # Blue
        'CS': '#1cc88a',      # Green
        'IT': '#1cc88a',      # Green
        'ENG': '#f6c23e',     # Yellow
        'EE': '#f6c23e',      # Yellow
        'HUM': '#e74a3b',     # Red
        'SOC': '#e74a3b'      # Red
    }
    
    for prefix, color in color_map.items():
        if course_code.startswith(prefix):
            return color
    
    return '#858796'  # Default gray

def calculate_total_sessions(schedule):
    """Calculate total sessions per week"""
    total = 0
    for day in schedule.values():
        for period in day.values():
            total += len(period)
    return total

def calculate_total_hours(schedule):
    """Calculate total hours per week"""
    total_hours = 0
    for day in schedule.values():
        for period, courses in day.items():
            if courses:
                total_hours += 0.75  # Each period is 45 minutes
    return round(total_hours, 1)

def get_first_class(courses):
    """Get first class of the week"""
    if not courses:
        return "Chưa có lịch học"
    
    # Mock implementation
    return "Thứ 2, Tiết 1 (7:00)"