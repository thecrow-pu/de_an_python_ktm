from typing import Dict
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# CSV file paths
CSV_PATHS = {
    "students": os.path.join(DATA_DIR, 'sinh_vien.csv'),
    "subjects": os.path.join(DATA_DIR, 'mon_hoc.csv')
}

# Subject definitions
SUBJECTS: Dict[str, str] = {
    'WD102': 'Thiết Kế Web',
    'DB103': 'Cơ Sở Dữ Liệu',
    'JS201': 'Java Spring',
    'MA100': 'Toán Rời Rạc',
    'CSLT': 'Cơ Sở Lập Trình',
    'TCC1': 'Toán Cao Cấp',
    'CTDL100': 'Cấu trúc dữ liệu',
    'LTUDM': 'Lập Trình Hướng Đối Tượng'
}

# Subject credits
SUBJECT_CREDITS: Dict[str, int] = {
    'WD102': 3,
    'DB103': 3,
    'JS201': 4,
    'MA100': 2,
    'CSLT': 3,
    'TCC1': 3,
    'CTDL100': 6,
    'LTUDM': 3
}

# Attendance status definitions
ATTENDANCE_STATUS: Dict[str, str] = {
    "1": "Có mặt",
    "2": "Vắng mặt",
    "3": "Đi trễ",
    "4": "Có phép",
    "5": "Không phép"
}

# Maximum allowed absences
MAX_ABSENCES = 4