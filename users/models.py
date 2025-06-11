from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField("이름", max_length=30, default="홍길동")
    student_id = models.CharField("학번", max_length=20, default="20250001")
    grade = models.CharField("학년", max_length=10, default="1")  # 1, 2, 3, 4로 구분
    gender = models.CharField("성별", max_length=10, default="남")  # "남", "여", "기타" 등
