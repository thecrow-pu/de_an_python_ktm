from typing import Dict, Optional, Union

class Student:
    def __init__(self, student_id: str, name: str, class_name: str, 
                school: str, department: str, enrollment_term: str):
        self.student_id = student_id  # ma_sv
        self.name = name  # ho_ten
        self.class_name = class_name  # lop_hoc
        self.school = school  # truong
        self.department = department  # khoa
        self.enrollment_term = enrollment_term  # hoc_ky_nhap_hoc
        self.attendance: Dict[str, Dict[str, str]] = {}
        
    def add_attendance(self, subject: str, date: str, status: str) -> None:
        """Thêm điểm danh cho sinh viên"""
        if subject not in self.attendance:
            self.attendance[subject] = {}
        self.attendance[subject][date] = status

    def update_attendance(self, subject: str, date: str, status: str) -> bool:
        """Cập nhật điểm danh cho sinh viên"""
        if date in self.attendance.get(subject, {}):
            self.attendance[subject][date] = status
            return True
        return False

    def get_attendance(self, subject: Optional[str] = None) -> Union[Dict[str, str], Dict[str, Dict[str, str]]]:
        """Lấy thông tin điểm danh của sinh viên"""
        if subject:
            return self.attendance.get(subject, {})
        return self.attendance

    def check_exam_eligibility(self, subject: str, max_absences: int) -> tuple[bool, int]:
        """Kiểm tra điều kiện dự thi của sinh viên"""
        if subject not in self.attendance:
            return True, 0
        absences = sum(1 for status in self.attendance[subject].values() 
                    if status in ["Vắng mặt", "Không phép"])
        return absences <= max_absences, absences

    def update_info(self, name: Optional[str] = None, age: Optional[int] = None, 
                email: Optional[str] = None, class_name: Optional[str] = None,
                major: Optional[str] = None) -> None:
        """Cập nhật thông tin sinh viên"""
        if name:
            self.name = name
        if age:
            self.age = age
        if email:
            self.email = email
        if class_name:
            self.class_name = class_name
        if major:
            self.major = major

    def __str__(self) -> str:
        """Hiển thị thông tin sinh viên"""
        return f"Mã số: {self.student_id}, Họ tên: {self.name}, Lớp: {self.class_name}, Ngành: {self.major}"