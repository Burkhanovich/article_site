"""
User models for the article publishing platform.
Custom user model with role-based access control for editorial workflow.
"""
import os
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom User model with roles for the editorial workflow.
    Roles: Reader, Author, Reviewer (Red Collegiya), Admin
    """

    class UserRole(models.TextChoices):
        READER = 'READER', _('Reader')
        AUTHOR = 'AUTHOR', _('Author')
        REVIEWER = 'REVIEWER', _('Reviewer')
        ADMIN = 'ADMIN', _('Administrator')

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        }
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.READER,
        verbose_name=_('Role')
    )

    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Biography')
    )

    organization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Organization')
    )

    has_accepted_rules = models.BooleanField(
        default=False,
        verbose_name=_('Has Accepted Article Rules')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_reader(self):
        return self.role == self.UserRole.READER

    @property
    def is_author(self):
        return self.role == self.UserRole.AUTHOR

    @property
    def is_reviewer(self):
        return self.role == self.UserRole.REVIEWER

    @property
    def is_admin_user(self):
        return self.role == self.UserRole.ADMIN or self.is_superuser

    @property
    def can_create_articles(self):
        """Check if user can create articles."""
        return self.role in [self.UserRole.AUTHOR, self.UserRole.ADMIN] or self.is_superuser

    @property
    def can_review_articles(self):
        """Check if user can review articles."""
        return self.role == self.UserRole.REVIEWER or self.is_superuser

    def get_assigned_categories(self):
        """Get categories assigned to this reviewer."""
        if self.is_reviewer or self.is_superuser:
            from articles.models import Category
            return Category.objects.filter(reviewers=self)
        return Category.objects.none()

    def can_review_category(self, category):
        """Check if user can review articles in a specific category."""
        if self.is_superuser:
            return True
        if not self.is_reviewer:
            return False
        return category.reviewers.filter(pk=self.pk).exists()


def article_rules_upload_path(instance, filename):
    """Generate upload path for article rules files."""
    return f'rules/{filename}'


def validate_rules_file(file):
    """Validate uploaded rules file."""
    allowed_extensions = ['.txt']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(_('Only .txt files are allowed for rules.'))

    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(_('Rules file size cannot exceed 5MB.'))


class ArticleRules(models.Model):
    """
    Model to store article writing rules for authors.
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
        return cls.objects.filter(is_active=True).first()

    def get_rules_content(self):
        if self.rules_file:
            try:
                with open(self.rules_file.path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return self.content or "Rules file could not be read."
        return self.content or "No rules available."

    def save(self, *args, **kwargs):
        if self.is_active:
            ArticleRules.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    In-site notification model for user alerts.
    """

    class NotificationType(models.TextChoices):
        REVIEWER_ASSIGNED = 'REVIEWER_ASSIGNED', _('Reviewer Assigned')
        ARTICLE_FOR_REVIEW = 'ARTICLE_FOR_REVIEW', _('Article For Review')
        REVIEW_SUBMITTED = 'REVIEW_SUBMITTED', _('Review Submitted')
        ARTICLE_PUBLISHED = 'ARTICLE_PUBLISHED', _('Article Published')
        ARTICLE_REJECTED = 'ARTICLE_REJECTED', _('Article Rejected')
        CHANGES_REQUESTED = 'CHANGES_REQUESTED', _('Changes Requested')
        STATUS_CHANGED = 'STATUS_CHANGED', _('Status Changed')
        GENERAL = 'GENERAL', _('General')

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        verbose_name=_('Type')
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )

    message = models.TextField(
        verbose_name=_('Message')
    )

    link = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Link')
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Read')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title[:50]}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user."""
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def get_recent(cls, user, limit=10):
        """Get recent notifications for a user."""
        return cls.objects.filter(user=user)[:limit]
