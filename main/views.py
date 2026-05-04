from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .forms import RegistrationForm, UserProfileForm, PasswordChangeForm
from .models import UserProfile


def register_view(request: HttpRequest) -> HttpResponse:
    """Handles user registration"""
    if request.user.is_authenticated:
        return redirect('profile_view')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful! You are now logged in.")
            login(request, user)
            return redirect('profile_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_view(request: HttpRequest, username: str = None) -> HttpResponse:
    """Displays the user profile. Shows the current user's profile if username is None"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    return render(request, 'profile.html', {'profile_user': user})


@login_required
def edit_profile_view(request: HttpRequest) -> HttpResponse:
    """Handles editing of the user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user.profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    """Handles password changing for an authenticated user"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def delete_account_view(request: HttpRequest) -> HttpResponse:
    """Deletes the user's account and logs them out (Optional Feature)"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been completely deleted.")
        return redirect('register_view')
    return render(request, 'confirm_delete.html')
