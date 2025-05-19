from datetime import datetime
import os
from typing import List
from models.student import Student
from models.subject import Subject
from services.attendance_system import AttendanceSystem, AttendanceHistory
from utils.constants import ATTENDANCE_STATUS, DATA_DIR

def print_menu() -> None:
    print("\n=== HỆ THỐNG QUẢN LÝ ĐIỂM DANH SINH VIÊN ===")
    print("1. Thêm sinh viên mới")
    print("2. Điểm danh")
    print("3. Tìm kiếm sinh viên")
    print("4. Xuất báo cáo điểm danh")
    print("5. Xem danh sách môn học")
    print("6. Chỉnh sửa điểm danh")
    print("7. Xem lịch sử điểm danh")
    print("8. Xuất báo cáo theo lớp")
    print("9. Thoát")
    print("==========================================")

def print_subjects(subjects: List[Subject]) -> None:
    print("\nDANH SÁCH MÔN HỌC:")
    print("Mã MH | Tên môn học                | Số tín chỉ")
    print("-" * 50)
    for subject in subjects:
        print(f"{subject.code:6} | {subject.name:24} | {subject.credits:10}")
    print("-" * 50)

def get_student_info() -> Student:
    student_id = input("Nhập MSSV: ")
    name = input("Nhập họ tên: ")
    class_name = input("Nhập lớp: ")
    school = input("Nhập trường: ")
    department = input("Nhập khoa: ")
    enrollment_term = input("Nhập học kỳ nhập học (VD: HK1-2024): ")
    return Student(student_id, name, class_name, school, department, enrollment_term)

def print_attendance_history(history: List[AttendanceHistory]) -> None:
    if not history:
        print("Không có lịch sử điểm danh!")
        return
        
    print("\nLỊCH SỬ ĐIỂM DANH:")
    print("Ngày       | Môn học | Trạng thái")
    print("-" * 40)
    for record in history:
        print(f"{record['date']} | {record['subject']:7} | {record['status']}")
    print("-" * 40)

def main() -> None:
    system = AttendanceSystem()
    data_file = os.path.join(DATA_DIR, 'sinh_vien.csv')
    
    # Tải dữ liệu sinh viên từ file CSV nếu có
    if os.path.exists(data_file):
        system.load_students_from_csv(data_file)

    while True:
        print_menu()
        choice = input("Nhập lựa chọn của bạn (1-9): ")

        if choice == "1":
            try:
                student = get_student_info()
                if system.add_student(student):
                    print(f"Đã thêm sinh viên {student.name} thành công!")
                    # Lưu ngay sau khi thêm
                    system.save_students_to_csv(data_file)
                else:
                    print("MSSV đã tồn tại!")
            except ValueError as e:
                print(f"Lỗi: {str(e)}")

        elif choice == "2":
            student_id = input("Nhập MSSV: ")
            if student_id not in system.students:
                print("Không tìm thấy sinh viên!")
                continue

            print_subjects(system.get_subject_list())
            subject_code = input("Nhập mã môn học: ")
            if subject_code not in system.subjects:
                print("Mã môn học không hợp lệ!")
                continue

            date = datetime.now().strftime("%Y-%m-%d")
            
            print("\nTrạng thái điểm danh:")
            for key, value in ATTENDANCE_STATUS.items():
                print(f"{key}. {value}")
            
            status_key = input("Chọn trạng thái (1-5): ")
            if status_key in ATTENDANCE_STATUS:
                if system.take_attendance(subject_code, date, student_id, ATTENDANCE_STATUS[status_key]):
                    print("Đã điểm danh thành công!")
                else:
                    print("Có lỗi xảy ra khi điểm danh!")
            else:
                print("Trạng thái không hợp lệ!")

        elif choice == "3":
            keyword = input("Nhập từ khóa tìm kiếm (MSSV, tên): ")
            results = system.search_student(keyword)
            if results:
                print("\nKết quả tìm kiếm:")
                print("MSSV     | Họ tên                      | Lớp      | Khoa")
                print("-" * 70)
                for student in results:
                    print(f"{student.student_id:8} | {student.name:26} | "
                          f"{student.class_name:9} | {student.department}")
            else:
                print("Không tìm thấy sinh viên nào!")

        elif choice == "4":
            print_subjects(system.get_subject_list())
            subject_code = input("Nhập mã môn học cần xuất báo cáo: ")
            
            if subject_code not in system.subjects:
                print("Mã môn học không hợp lệ!")
                continue
                
            try:
                start_date = datetime.strptime(
                    input("Nhập ngày bắt đầu (dd/mm/yyyy): "), "%d/%m/%Y"
                )
                end_date = datetime.strptime(
                    input("Nhập ngày kết thúc (dd/mm/yyyy): "), "%d/%m/%Y"
                )
                
                report = system.generate_report(subject_code, start_date, end_date)
                filename = f"bao_cao_{subject_code}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                
                saved_path = system.save_report(report, filename)
                if saved_path:
                    print(f"Đã xuất báo cáo thành công! File: {saved_path}")
                else:
                    print("Có lỗi xảy ra khi xuất báo cáo!")
                    
            except ValueError as e:
                print(f"Lỗi: Định dạng ngày không hợp lệ! ({str(e)})")

        elif choice == "5":
            print_subjects(system.get_subject_list())

        elif choice == "6":
            student_id = input("Nhập MSSV: ")
            if student_id not in system.students:
                print("Không tìm thấy sinh viên!")
                continue

            print_subjects(system.get_subject_list())
            subject_code = input("Nhập mã môn học: ")
            if subject_code not in system.subjects:
                print("Mã môn học không hợp lệ!")
                continue

            date = input("Nhập ngày cần sửa (dd/mm/yyyy): ")
            try:
                datetime.strptime(date, "%d/%m/%Y")
                date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                print("Định dạng ngày không hợp lệ!")
                continue

            print("\nTrạng thái điểm danh mới:")
            for key, value in ATTENDANCE_STATUS.items():
                print(f"{key}. {value}")
            
            status_key = input("Chọn trạng thái mới (1-5): ")
            if status_key in ATTENDANCE_STATUS:
                if system.edit_attendance(subject_code, student_id, date, ATTENDANCE_STATUS[status_key]):
                    print("Đã cập nhật điểm danh thành công!")
                else:
                    print("Có lỗi xảy ra khi cập nhật điểm danh!")
            else:
                print("Trạng thái không hợp lệ!")

        elif choice == "7":
            student_id = input("Nhập MSSV: ")
            if student_id not in system.students:
                print("Không tìm thấy sinh viên!")
                continue

            show_specific = input("Xem môn học cụ thể? (C/K): ").upper() == 'C'
            
            if show_specific:
                print_subjects(system.get_subject_list())
                subject_code = input("Nhập mã môn học: ")
                if subject_code not in system.subjects:
                    print("Mã môn học không hợp lệ!")
                    continue
                history = system.get_student_attendance_history(student_id, subject_code)
            else:
                history = system.get_student_attendance_history(student_id)
            
            print_attendance_history(history)

        elif choice == "8":
            print_subjects(system.get_subject_list())
            subject_code = input("Nhập mã môn học cần xuất báo cáo: ")
            
            if subject_code not in system.subjects:
                print("Mã môn học không hợp lệ!")
                continue
            
            class_name = input("Nhập tên lớp: ")
                
            try:
                start_date = datetime.strptime(
                    input("Nhập ngày bắt đầu (dd/mm/yyyy): "), "%d/%m/%Y"
                )
                end_date = datetime.strptime(
                    input("Nhập ngày kết thúc (dd/mm/yyyy): "), "%d/%m/%Y"
                )
                
                report = system.get_class_report(subject_code, class_name, start_date, end_date)
                filename = f"bao_cao_{subject_code}_{class_name}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                
                saved_path = system.save_report(report, filename)
                if saved_path:
                    print(f"Đã xuất báo cáo thành công! File: {saved_path}")
                else:
                    print("Có lỗi xảy ra khi xuất báo cáo!")
                    
            except ValueError as e:
                print(f"Lỗi: Định dạng ngày không hợp lệ! ({str(e)})")

        elif choice == "9":
            print("Cảm ơn bạn đã sử dụng hệ thống!")
            break

        else:
            print("Lựa chọn không hợp lệ! Vui lòng chọn lại.")

if __name__ == "__main__":
    main()