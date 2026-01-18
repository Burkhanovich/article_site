"""
Article models for the publishing platform.
"""
import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField


def article_cover_upload_path(instance, filename):
    """
    Generate upload path for article cover images.
    Format: articles/covers/{author_username}/{filename}
    """
    return f'articles/covers/{instance.author.username}/{filename}'


def validate_image_size(image):
    """
    Validate uploaded image size (max 5MB).
    """
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)  # 5MB default

    if image.size > max_size:
        raise ValidationError(
            f'Image file size cannot exceed {max_size / (1024 * 1024)}MB. '
            f'Current size: {image.size / (1024 * 1024):.2f}MB'
        )


def article_file_upload_path(instance, filename):
    """
    Generate upload path for article files.
    Format: articles/files/{author_username}/{filename}
    """
    return f'articles/files/{instance.author.username}/{filename}'


def validate_article_file(file):
    """
    Validate uploaded article file.
    Allowed formats: .txt, .doc, .docx, .pdf
    Max size: 10MB
    """
    # Allowed extensions
    allowed_extensions = ['.txt', '.doc', '.docx', '.pdf']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            _('Only .txt, .doc, .docx, and .pdf files are allowed.')
        )

    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(
            f'Article file size cannot exceed 10MB. '
            f'Current size: {file.size / (1024 * 1024):.2f}MB'
        )

    # Security check: verify it's actually a valid file
    try:
        # Read first few bytes to check file signature
        file.seek(0)
        header = file.read(8)
        file.seek(0)  # Reset file pointer

        # Check for malicious patterns (very basic check)
        dangerous_patterns = [b'<?php', b'<script', b'#!/bin/']
        for pattern in dangerous_patterns:
            if pattern in header:
                raise ValidationError(
                    _('Potentially dangerous file detected.')
                )
    except Exception as e:
        # If we can't read the file, it's suspicious
        if 'dangerous' not in str(e):
            raise ValidationError(_('Invalid file format.'))


class Article(models.Model):
    """
    Article model with rich text content and cover image.
    """

    class ArticleStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')

    # Basic fields
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
        help_text=_('Article title (max 200 characters)')
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        verbose_name=_('Slug'),
        help_text=_('Auto-generated from title, used in URLs')
    )

    # Rich text content with CKEditor
    content = RichTextUploadingField(
        verbose_name=_('Content'),
        help_text=_('Article content with rich text formatting')
    )

    # Cover image
    cover_image = models.ImageField(
        upload_to=article_cover_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS
            ),
            validate_image_size
        ],
        verbose_name=_('Cover Image'),
        help_text=_(
            f"Allowed formats: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}. "
            f"Max size: {settings.MAX_IMAGE_SIZE / (1024 * 1024)}MB"
        )
    )

    # Article file upload
    article_file = models.FileField(
        upload_to=article_file_upload_path,
        blank=True,
        null=True,
        validators=[validate_article_file],
        verbose_name=_('Article File'),
        help_text=_('Upload article as file (.txt, .doc, .docx, .pdf - max 10MB)')
    )

    # Status
    status = models.CharField(
        max_length=10,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        verbose_name=_('Status')
    )

    # Relationships
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('Author')
    )

    # View counter (bonus feature)
    views = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Views'),
        help_text=_('Number of times this article has been viewed')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate unique slug from title.
        """
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """
        Generate unique slug from title.
        Append number if slug already exists.
        """
        base_slug = slugify(self.title)
        unique_slug = base_slug
        counter = 1

        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{base_slug}-{counter}'
            counter += 1

        return unique_slug

    def increment_views(self):
        """
        Increment article view counter.
        """
        self.views += 1
        self.save(update_fields=['views'])

    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == self.ArticleStatus.PUBLISHED

    def get_absolute_url(self):
        """Get article detail URL."""
        from django.urls import reverse
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def delete(self, *args, **kwargs):
        """
        Override delete to remove cover image and article file from storage.
        """
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)

        if self.article_file:
            if os.path.isfile(self.article_file.path):
                os.remove(self.article_file.path)

        super().delete(*args, **kwargs)

    def get_file_size(self):
        """Get article file size in MB."""
        if self.article_file:
            return round(self.article_file.size / (1024 * 1024), 2)
        return 0

    def get_file_extension(self):
        """Get article file extension."""
        if self.article_file:
            return os.path.splitext(self.article_file.name)[1].upper().replace('.', '')
        return None
