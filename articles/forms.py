"""
Forms for article creation and editing with editorial workflow.
"""
import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Article, Category, Keyword, Review


ALLOWED_FILE_EXTENSIONS = ['pdf', 'doc', 'docx']
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles.
    Authors cannot directly set status - they can only save as draft or submit for review.
    """

    # Hidden field to collect keywords as JSON list from JS
    keywords_json = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'keywords-json-input'}),
        required=False,
    )

    class Meta:
        model = Article
        fields = [
            'title_uz', 'title_ru', 'title_en',
            'content_uz', 'content_ru', 'content_en',
            'article_file',
            'categories', 'review_mode'
        ]
        widgets = {
            'title_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter title in Uzbek'),
                'maxlength': '300'
            }),
            'title_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter title in Russian (optional)'),
                'maxlength': '300'
            }),
            'title_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter title in English (optional)'),
                'maxlength': '300'
            }),
            'content_uz': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Write article content in Uzbek')
            }),
            'content_ru': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Write article content in Russian (optional)')
            }),
            'content_en': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Write article content in English (optional)')
            }),
            'article_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'review_mode': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set translated labels
        self.fields['title_uz'].label = _('Title (Uzbek)')
        self.fields['title_ru'].label = _('Title (Russian)')
        self.fields['title_en'].label = _('Title (English)')
        self.fields['content_uz'].label = _('Content (Uzbek)')
        self.fields['content_ru'].label = _('Content (Russian)')
        self.fields['content_en'].label = _('Content (English)')
        self.fields['article_file'].label = _('Article File')
        self.fields['categories'].label = _('Categories')
        self.fields['review_mode'].label = _('Review Mode')

        # Make only Uzbek fields required
        self.fields['title_ru'].required = False
        self.fields['title_en'].required = False
        self.fields['content_ru'].required = False
        self.fields['content_en'].required = False

        # Filter only active categories
        self.fields['categories'].queryset = Category.objects.filter(is_active=True)

        # Pre-populate keywords JSON if editing
        if self.instance.pk:
            import json
            kw_list = list(self.instance.keywords.values_list('name', flat=True))
            self.fields['keywords_json'].initial = json.dumps(kw_list)

    def clean_title_uz(self):
        """Validate Uzbek title is not empty and not too long."""
        title = self.cleaned_data.get('title_uz')

        if not title or not title.strip():
            raise ValidationError(_('Title cannot be empty.'))

        if len(title) > 300:
            raise ValidationError(_('Title cannot exceed 300 characters.'))

        return title.strip()

    def clean_content_uz(self):
        """Validate Uzbek content is not empty."""
        content = self.cleaned_data.get('content_uz')

        if not content or not content.strip():
            raise ValidationError(_('Content cannot be empty.'))

        return content.strip()

    def clean_categories(self):
        """Validate at least one category is selected."""
        categories = self.cleaned_data.get('categories')

        if not categories or categories.count() == 0:
            raise ValidationError(_('Please select at least one category.'))

        return categories

    def clean_article_file(self):
        """Validate article file."""
        f = self.cleaned_data.get('article_file')

        if f:
            ext = os.path.splitext(f.name)[1].lstrip('.').lower()
            if ext not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    _('Allowed file types: %(types)s') % {
                        'types': ', '.join(ALLOWED_FILE_EXTENSIONS)
                    }
                )

            if f.size > MAX_FILE_SIZE:
                raise ValidationError(
                    _('File size must not exceed %(size)s MB.') % {
                        'size': MAX_FILE_SIZE // (1024 * 1024)
                    }
                )

        return f

    def clean_keywords_json(self):
        """Parse and validate keywords JSON."""
        import json
        raw = self.cleaned_data.get('keywords_json', '').strip()

        if not raw:
            raise ValidationError(_('Please add at least one keyword.'))

        try:
            keywords = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            raise ValidationError(_('Invalid keyword data.'))

        if not isinstance(keywords, list):
            raise ValidationError(_('Invalid keyword data.'))

        # Filter empty values
        keywords = [kw.strip() for kw in keywords if kw and kw.strip()]

        if len(keywords) < 1:
            raise ValidationError(_('Please add at least one keyword.'))

        return keywords

    def save(self, commit=True):
        """Save article and set keywords."""
        article = super().save(commit=commit)

        if commit:
            # Set keywords from the parsed JSON list
            keyword_names = self.cleaned_data.get('keywords_json', [])
            if isinstance(keyword_names, list) and keyword_names:
                kw_string = ', '.join(keyword_names)
                article.set_keywords_from_string(kw_string)
            else:
                article.keywords.clear()

        return article


class ReviewForm(forms.ModelForm):
    """
    Form for reviewers to submit reviews.
    """

    class Meta:
        model = Review
        fields = ['decision', 'comment']
        widgets = {
            'decision': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Add your review comments here...')
            }),
        }

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

        self.fields['decision'].label = _('Your Decision')
        self.fields['comment'].label = _('Comment')

        # Add help text based on category policy
        if category:
            try:
                policy = category.policy
                if policy.require_changes_comment or policy.require_reject_comment:
                    self.fields['comment'].help_text = _(
                        'Comment is required when requesting changes or rejecting.'
                    )
            except Exception:
                pass

    def clean(self):
        """Validate comment based on category policy."""
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        comment = cleaned_data.get('comment')

        if self.category:
            try:
                policy = self.category.policy
                if decision == Review.Decision.CHANGES and policy.require_changes_comment:
                    if not comment or not comment.strip():
                        raise ValidationError(
                            _('Please provide a comment explaining what changes are needed.')
                        )
                if decision == Review.Decision.REJECT and policy.require_reject_comment:
                    if not comment or not comment.strip():
                        raise ValidationError(
                            _('Please provide a comment explaining the reason for rejection.')
                        )
            except Exception:
                pass

        return cleaned_data


class ArticleSearchForm(forms.Form):
    """
    Form for searching published articles.
    """

    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by title, content, keywords...'),
            'aria-label': 'Search'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_('All Categories'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
