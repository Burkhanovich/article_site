"""
User models for the article publishing platform.
Custom user model with role-based access control.
"""
import os
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control (Reader/Author).
    """

    class UserRole(models.TextChoices):
        READER = 'READER', _("O'quvchi (Reader)")
        AUTHOR = 'AUTHOR', _('Avtor (Author)')

    # Override email to make it unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )

    # User role field
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.READER,
        verbose_name=_('User Role')
    )

    # Track if author has accepted rules
    has_accepted_rules = models.BooleanField(
        default=False,
        verbose_name=_('Has Accepted Article Rules')
    )

    # Additional fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_author(self):
        """Check if user is an author."""
        return self.role == self.UserRole.AUTHOR

    @property
    def is_reader(self):
        """Check if user is a reader."""
        return self.role == self.UserRole.READER

    @property
    def can_create_articles(self):
        """Check if user can create articles (Author who accepted rules)."""
        return self.is_author and self.has_accepted_rules

    def save(self, *args, **kwargs):
        """Override save to ensure readers don't have article creation rights."""
        if self.is_reader:
            self.has_accepted_rules = False
        super().save(*args, **kwargs)


def article_rules_upload_path(instance, filename):
    """Generate upload path for article rules files."""
    return f'rules/{filename}'


def validate_rules_file(file):
    """Validate uploaded rules file."""
    # Check file extension
    allowed_extensions = ['.txt']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            _('Only .txt files are allowed for rules.')
        )

    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(
            _('Rules file size cannot exceed 5MB.')
        )


class ArticleRules(models.Model):
    """
    Model to store article writing rules.
    Rules can be uploaded as .txt file or entered as text.
    Editable via admin panel, displayed to authors during onboarding.
    """

    title = models.CharField(
        max_length=200,
        default="Article Writing Rules",
        verbose_name=_('Title')
    )

    content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Rules Content'),
        help_text=_('Article writing guidelines (text format)')
    )

    rules_file = models.FileField(
        upload_to=article_rules_upload_path,
        blank=True,
        null=True,
        validators=[validate_rules_file],
        verbose_name=_('Rules File'),
        help_text=_('Upload rules as .txt file (optional, max 5MB)')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Only one set of rules should be active at a time')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Article Rules')
        verbose_name_plural = _('Article Rules')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @classmethod
    def get_active_rules(cls):
        """Get the currently active rules."""
        return cls.objects.filter(is_active=True).first()

    def get_rules_content(self):
        """Get rules content from file or text field."""
        if self.rules_file:
            try:
                with open(self.rules_file.path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return self.content or "Rules file could not be read."
        return self.content or "No rules available."

    def save(self, *args, **kwargs):
        """Ensure only one set of rules is active at a time."""
        if self.is_active:
            # Deactivate all other rules
            ArticleRules.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete rules file when model is deleted."""
        if self.rules_file:
            if os.path.isfile(self.rules_file.path):
                os.remove(self.rules_file.path)
        super().delete(*args, **kwargs)
