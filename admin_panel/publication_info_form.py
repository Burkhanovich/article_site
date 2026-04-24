"""
Form for managing article publication information (year and number).
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from articles.models import Article


class ArticlePublicationInfoForm(forms.ModelForm):
    """
    Form for admin to set publication year and number for articles.
    """
    
    class Meta:
        model = Article
        fields = ['publication_year', 'publication_number']
        widgets = {
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter publication year (e.g., 2024)'),
                'min': '1900',
                'max': '2100',
                'data-test': 'publication-year'
            }),
            'publication_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter publication number (e.g., 1, 2, 3...)'),
                'min': '1',
                'data-test': 'publication-number'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publication_year'].label = _('Publication Year')
        self.fields['publication_year'].required = False
        self.fields['publication_number'].label = _('Publication Number')
        self.fields['publication_number'].required = False
        
        # Add help text
        self.fields['publication_year'].help_text = _('Optional: Year the article was published')
        self.fields['publication_number'].help_text = _('Optional: Publication issue number')
