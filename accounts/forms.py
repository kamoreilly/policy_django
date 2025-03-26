from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # User starts inactive until approved
        if commit:
            user.save()
            # Set approval status to pending
            user.profile.approval_status = 'pending'
            user.profile.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department', 'bio']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.USER_ROLES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    approval_status = forms.ChoiceField(
        choices=UserProfile.APPROVAL_STATUS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['role'].initial = self.instance.profile.role
            self.fields['department'].initial = self.instance.profile.department
            self.fields['approval_status'].initial = self.instance.profile.approval_status
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.profile.role = self.cleaned_data['role']
            user.profile.department = self.cleaned_data['department']
            user.profile.approval_status = self.cleaned_data['approval_status']
            # Only activate user if approved
            user.is_active = self.cleaned_data['is_active'] and self.cleaned_data['approval_status'] == 'approved'
            user.save()
            user.profile.save()
        return user