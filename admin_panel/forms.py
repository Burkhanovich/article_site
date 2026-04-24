"""
Admin panel forms for managing reviewers, articles, and system settings.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from articles.models import Article, Review, Journal
from users.models import CustomUser

User = get_user_model()


class ReviewerCreationForm(forms.ModelForm):
    """Form for creating new reviewer users."""
    
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter password'),
            'data-test': 'password1'
        })
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm password'),
            'data-test': 'password2'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'organization', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Username'),
                'data-test': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email address'),
                'data-test': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First name'),
                'data-test': 'first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last name'),
                'data-test': 'last_name'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Organization'),
                'data-test': 'organization'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Biography'),
                'rows': 4,
                'data-test': 'bio'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('Passwords do not match.'))
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.UserRole.REVIEWER
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
        return user


class ReviewerEditForm(forms.ModelForm):
    """Form for editing existing reviewer users."""

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'organization', 'bio', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'data-test': 'username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'data-test': 'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'data-test': 'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'data-test': 'last_name'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'data-test': 'organization'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'data-test': 'bio'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-test': 'is_active'
            }),
        }




class ReviewerAssignmentForm(forms.Form):
    """Form for assigning reviewers to an article."""

    reviewers = forms.ModelMultipleChoiceField(
        label=_('Select Reviewers'),
        queryset=CustomUser.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '10',
            'data-test': 'assignment-reviewers'
        }),
        help_text=_('Hold Ctrl or Cmd to select multiple reviewers')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].queryset = User.objects.filter(
            role=CustomUser.UserRole.REVIEWER,
            is_active=True
        ).order_by('first_name', 'last_name', 'username')


class ArticleActionForm(forms.Form):
    """Form for admin actions on articles (publish, reject, etc.) and set publication info."""
    
    ACTION_CHOICES = [
        ('publish', _('Publish Article')),
        ('reject', _('Reject Article')),
        ('request_changes', _('Request Changes')),
        ('reset_status', _('Reset to In Review')),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        label=_('Action'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-test': 'action-select'
        })
    )
    
    note = forms.CharField(
        label=_('Admin Note'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Enter admin note (visible to author)'),
            'data-test': 'admin-note'
        })
    )
    
    publication_year = forms.IntegerField(
        label=_('Publication Year'),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('E.g., 2024'),
            'min': '1900',
            'max': '2100',
            'data-test': 'publication-year'
        })
    )
    
    publication_number = forms.IntegerField(
        label=_('Publication Number'),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('E.g., 1, 2, 3...'),
            'min': '1',
            'data-test': 'publication-number'
        })
    )


class BulkArticleActionForm(forms.Form):
    """Form for bulk article actions."""
    
    ACTION_CHOICES = [
        ('publish', _('Publish Selected')),
        ('reject', _('Reject Selected')),
        ('request_changes', _('Request Changes on Selected')),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-test': 'bulk-action'
        })
    )
    
    note = forms.CharField(
        label=_('Note (for rejection/changes)'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'data-test': 'bulk-note'
        })
    )


class JournalForm(forms.ModelForm):
    """Form for managing journals."""
    
    class Meta:
        model = Journal
        fields = ['year', 'number', 'is_active']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
