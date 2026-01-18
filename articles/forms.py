"""
Forms for article creation and editing.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Article


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles.
    """

    class Meta:
        model = Article
        fields = ['title', 'content', 'cover_image', 'article_file', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title',
                'maxlength': '200'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'article_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.txt,.doc,.docx,.pdf'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set translated labels
        self.fields['title'].label = _('Article Title')
        self.fields['content'].label = _('Article Content')
        self.fields['cover_image'].label = _('Cover Image')
        self.fields['article_file'].label = _('Article File')
        self.fields['status'].label = _('Status')

        # Add translated help text
        self.fields['title'].help_text = _('Maximum 200 characters')
        self.fields['content'].help_text = _('Write your article content with rich text formatting')
        self.fields['cover_image'].help_text = _(
            'Allowed formats: JPG, PNG, GIF, WebP. Maximum size: 5MB'
        )
        self.fields['article_file'].help_text = _(
            'Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB'
        )
        self.fields['status'].help_text = _(
            'Choose "Draft" to save without publishing, or "Published" to make it visible to readers'
        )

        # Make cover image and article file optional
        self.fields['cover_image'].required = False
        self.fields['article_file'].required = False

    def clean_title(self):
        """Validate title is not empty and not too long."""
        title = self.cleaned_data.get('title')

        if not title or not title.strip():
            raise ValidationError('Title cannot be empty.')

        if len(title) > 200:
            raise ValidationError('Title cannot exceed 200 characters.')

        return title.strip()

    def clean_cover_image(self):
        """Validate cover image format and size."""
        cover_image = self.cleaned_data.get('cover_image')

        if not cover_image:
            return cover_image

        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        ext = cover_image.name.split('.')[-1].lower()

        if ext not in allowed_extensions:
            raise ValidationError(
                f'Invalid file format. Allowed: {", ".join(allowed_extensions)}'
            )

        # Check file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB
        if cover_image.size > max_size:
            raise ValidationError(
                f'Image size too large. Maximum size is 5MB. '
                f'Current size: {cover_image.size / (1024 * 1024):.2f}MB'
            )

        return cover_image


class ArticleSearchForm(forms.Form):
    """
    Form for searching articles.
    """

    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles...',
            'aria-label': 'Search'
        })
    )
