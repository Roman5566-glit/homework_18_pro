from typing import Any, Dict
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile


class RegistrationForm(forms.ModelForm):
    """Form for user registration with password confirmation and unique email validation"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self) -> str:
        """Validates that the email is unique"""
        email: str = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self) -> Dict[str, Any]:
        """Validates that both passwords match"""
        cleaned_data: Dict[str, Any] = super().clean()
        password: str = cleaned_data.get('password', '')
        confirm_password: str = cleaned_data.get('confirm_password', '')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile details including a 2MB limit on the avatar"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'birth_date', 'location', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self) -> Any:
        """Validates that the uploaded avatar size does not exceed 2MB"""
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            max_size = 2 * 1024 * 1024  # 2 Megabytes
            if avatar.size > max_size:
                raise forms.ValidationError("Image file is too large (must be under 2MB).")
        return avatar


class PasswordChangeForm(forms.Form):
    """Form for changing the user's password with validation of the current password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user: User, *args, **kwargs) -> None:
        """Initializes the form with the current user object."""
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self) -> str:
        """Validates the current password"""
        current_password: str = self.cleaned_data.get('current_password', '')
        if not authenticate(username=self.user.username, password=current_password):
            raise forms.ValidationError("Invalid current password.")
        return current_password

    def clean(self) -> Dict[str, Any]:
        """Validates new password confirmation and checks it's different from the current one"""
        cleaned_data: Dict[str, Any] = super().clean()
        new_password: str = cleaned_data.get('new_password', '')
        confirm_new_password: str = cleaned_data.get('confirm_new_password', '')
        current_password: str = cleaned_data.get('current_password', '')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError("New passwords do not match.")
            if new_password == current_password:
                raise forms.ValidationError("New password cannot be the same as the current password.")
        return cleaned_data
    