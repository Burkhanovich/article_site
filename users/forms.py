"""
Forms for user authentication and registration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    """
    Custom registration form with role selection.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )

    # Only allow READER and AUTHOR for public registration
    # REVIEWER and ADMIN roles must be assigned by administrators
    REGISTRATION_ROLE_CHOICES = [
        (CustomUser.UserRole.READER, 'Reader'),
        (CustomUser.UserRole.AUTHOR, 'Author'),
    ]

    role = forms.ChoiceField(
        choices=REGISTRATION_ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial=CustomUser.UserRole.READER,
        label='Select your role'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        """Save user with selected role."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']

        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling.
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class ArticleRulesAcceptanceForm(forms.Form):
    """
    Form for authors to accept article writing rules.
    """

    accept_rules = forms.BooleanField(
        required=True,
        label='I have read and accept the article writing rules',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'You must accept the rules before creating articles.'
        }
    )
