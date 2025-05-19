from typing import List, Dict, TypedDict, Union, Optional
import csv
from datetime import datetime
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject
from utils.constants import ATTENDANCE_STATUS, MAX_ABSENCES, CSV_PATHS

class StudentReport(TypedDict):
    student_id: str
    name: str
    absences: int
    late_arrivals: int
    present: int
    eligible_for_exam: bool

class AttendanceReport(TypedDict):
    subject: str
    period: str
    students: List[StudentReport]

class AttendanceHistory(TypedDict):
    subject: str
    date: str
    status: str

class AttendanceSystem:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.subjects: Dict[str, Subject] = {}
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Load subjects when initialized
        self.load_subjects_from_csv(CSV_PATHS["subjects"])

    def add_student(self, student: Student) -> bool:
        """Thêm sinh viên mới vào hệ thống"""
        if student.student_id not in self.students:
            self.students[student.student_id] = student
            return True
        return False

    def load_students_from_csv(self, file_path: str) -> None:
        """Đọc dữ liệu sinh viên từ file CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student = Student(
                        student_id=row['ma_sv'],
                        name=row['ho_ten'],
                        class_name=row['lop_hoc'],
                        school=row['truong'],
                        department=row['khoa'],
                        enrollment_term=row['hoc_ky_nhap_hoc']
                    )
                    self.add_student(student)
        except FileNotFoundError:
            print(f"File {file_path} không tồn tại")
        except Exception as e:
            print(f"Lỗi khi đọc file: {str(e)}")

    def save_students_to_csv(self, file_path: str) -> None:
        """Lưu dữ liệu sinh viên vào file CSV"""
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ma_sv', 'ho_ten', 'lop_hoc', 'truong', 'khoa', 'hoc_ky_nhap_hoc'])
                for student in self.students.values():
                    writer.writerow([
                        student.student_id,
                        student.name,
                        student.class_name,
                        student.school,
                        student.department,
                        student.enrollment_term
                    ])
        except Exception as e:
            print(f"Lỗi khi lưu file: {str(e)}")

    def load_subjects_from_csv(self, file_path: str) -> None:
        """Đọc danh sách môn học từ file CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    subject = Subject(
                        code=row['ma_mh'],
                        name=row['ten_mh'],
                        credits=int(row['so_tin_chi'])
                    )
                    self.subjects[subject.code] = subject
        except FileNotFoundError:
            print(f"File {file_path} không tồn tại")
        except Exception as e:
            print(f"Lỗi khi đọc file môn học: {str(e)}")

    def take_attendance(self, subject: str, date: str, student_id: str, status: str) -> bool:
        """Điểm danh cho sinh viên"""
        if status not in ATTENDANCE_STATUS.values():
            return False
        
        student = self.students.get(student_id)
        if student:
            student.add_attendance(subject, date, status)
            return True
        return False

    def edit_attendance(self, subject_code: str, student_id: str, date: str, new_status: str) -> bool:
        """Chỉnh sửa điểm danh của sinh viên"""
        if subject_code not in self.subjects:
            print("Mã môn học không hợp lệ!")
            return False
            
        if new_status not in ATTENDANCE_STATUS.values():
            print("Trạng thái điểm danh không hợp lệ!")
            return False
        
        student = self.students.get(student_id)
        if not student:
            print("Không tìm thấy sinh viên!")
            return False
            
        return student.update_attendance(subject_code, date, new_status)

    def search_student(self, keyword: str) -> List[Student]:
        """Tìm kiếm sinh viên theo từ khóa"""
        keyword = keyword.lower()
        return [
            student for student in self.students.values()
            if keyword in student.name.lower() or
            keyword in student.student_id.lower()
        ]

    def get_student_attendance_history(self, student_id: str, subject_code: Optional[str] = None) -> List[AttendanceHistory]:
        """Xem lịch sử điểm danh của sinh viên"""
        student = self.students.get(student_id)
        if not student:
            return []
            
        history: List[AttendanceHistory] = []
        attendance_records = student.get_attendance(subject_code) if subject_code else student.get_attendance()
        
        if subject_code:
            # Lịch sử cho một môn học cụ thể
            for date, status in attendance_records.items():
                history.append({
                    'subject': subject_code,
                    'date': date,
                    'status': status
                })
        else:
            # Lịch sử cho tất cả các môn học
            for subj, dates in attendance_records.items():
                for date, status in dates.items():
                    history.append({
                        'subject': subj,
                        'date': date,
                        'status': status
                    })
        
        # Sắp xếp theo ngày, mới nhất lên đầu
        return sorted(history, key=lambda x: x['date'], reverse=True)

    def generate_report(self, subject: str, start_date: datetime, end_date: datetime) -> AttendanceReport:
        """Tạo báo cáo điểm danh theo khoảng thời gian"""
        report: AttendanceReport = {
            'subject': subject,
            'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            'students': []
        }

        for student in self.students.values():
            attendance_records = student.get_attendance(subject)
            absences = 0
            late_arrivals = 0
            present = 0

            for date, status in attendance_records.items():
                record_date = datetime.strptime(date, '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    if status in ['Vắng mặt', 'Không phép']:
                        absences += 1
                    elif status == 'Đi trễ':
                        late_arrivals += 1
                    elif status == 'Có mặt':
                        present += 1

            eligible_for_exam, _ = student.check_exam_eligibility(subject, MAX_ABSENCES)
            
            student_report: StudentReport = {
                'student_id': student.student_id,
                'name': student.name,
                'absences': absences,
                'late_arrivals': late_arrivals,
                'present': present,
                'eligible_for_exam': eligible_for_exam
            }
            report['students'].append(student_report)

        return report

    def get_class_report(self, subject_code: str, class_name: str, 
                        start_date: datetime, end_date: datetime) -> AttendanceReport:
        """Tạo báo cáo điểm danh theo lớp học"""
        report: AttendanceReport = {
            'subject': subject_code,
            'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            'students': []
        }

        # Lọc sinh viên theo lớp
        class_students = [s for s in self.students.values() if s.class_name == class_name]
        
        for student in class_students:
            attendance_records = student.get_attendance(subject_code)
            absences = 0
            late_arrivals = 0
            present = 0

            for date, status in attendance_records.items():
                record_date = datetime.strptime(date, '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    if status in ['Vắng mặt', 'Không phép']:
                        absences += 1
                    elif status == 'Đi trễ':
                        late_arrivals += 1
                    elif status == 'Có mặt':
                        present += 1

            eligible_for_exam, _ = student.check_exam_eligibility(subject_code, MAX_ABSENCES)
            
            student_report: StudentReport = {
                'student_id': student.student_id,
                'name': student.name,
                'absences': absences,
                'late_arrivals': late_arrivals,
                'present': present,
                'eligible_for_exam': eligible_for_exam
            }
            report['students'].append(student_report)

        return report

    def save_report(self, report: AttendanceReport, filename: str) -> str:
        """Lưu báo cáo vào file CSV"""
        file_path = os.path.join(self.reports_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(['Môn học:', report['subject']])
                writer.writerow(['Thời gian:', report['period']])
                writer.writerow([])
                writer.writerow(['MSSV', 'Họ tên', 'Vắng', 'Đi trễ', 'Có mặt', 'Đủ điều kiện thi'])
                
                # Write student data
                for student in report['students']:
                    writer.writerow([
                        student['student_id'],
                        student['name'],
                        student['absences'],
                        student['late_arrivals'],
                        student['present'],
                        'Có' if student['eligible_for_exam'] else 'Không'
                    ])
            return file_path
        except Exception as e:
            print(f"Lỗi khi lưu báo cáo: {str(e)}")
            return ""

    def get_subject_list(self) -> List[Subject]:
        """Lấy danh sách môn học"""
        return list(self.subjects.values())