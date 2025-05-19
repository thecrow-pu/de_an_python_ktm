from typing import Dict

class Subject:
    def __init__(self, code: str, name: str, credits: int):
        self.code = code  # ma_mh
        self.name = name  # ten_mh
        self.credits = credits  # so_tin_chi

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.credits} tín chỉ)"
