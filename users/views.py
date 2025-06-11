from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        return redirect('signup')
    return render(request, 'registration/delete_account.html')

@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
        # 필드별로 입력값 반영
        user.name = request.POST.get('name', user.name)
        user.student_id = request.POST.get('student_id', user.student_id)
        user.grade = request.POST.get('grade', user.grade)
        user.gender = request.POST.get('gender', user.gender)
        user.save()
        return redirect('profile')
    return render(request, 'profile.html', {'user': user})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
