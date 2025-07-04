from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(label="이름", max_length=30, widget=forms.TextInput(attrs={'class': 'input-box'}))
    student_id = forms.CharField(label="학번", max_length=20, widget=forms.TextInput(attrs={'class': 'input-box'}))
    grade = forms.ChoiceField(label="학년", choices=[('1', '1학년'), ('2', '2학년'), ('3', '3학년'), ('4', '4학년')], widget=forms.Select(attrs={'class': 'input-box'}))
    gender = forms.ChoiceField(label="성별", choices=[('남', '남'), ('여', '여'), ('기타', '기타')], widget=forms.Select(attrs={'class': 'input-box'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "name", "student_id", "grade", "gender")
