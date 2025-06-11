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
    if request.method == "POST":
        preferred = request.POST.get('preferred_professor')
        request.user.preferred_professor = preferred
        request.user.save()
    return render(request, 'profile.html', {'user': request.user})

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
