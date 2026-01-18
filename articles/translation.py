"""
Translation configuration for Article model.
Registers fields that should be translatable in multiple languages.
"""
from modeltranslation.translator import translator, TranslationOptions
from .models import Article


class ArticleTranslationOptions(TranslationOptions):
    """
    Define which fields should be translatable.
    This will create title_uz, title_ru, title_en, content_uz, content_ru, content_en fields.
    """
    fields = ('title', 'content')
    required_languages = ('uz',)  # Only Uzbek is required


translator.register(Article, ArticleTranslationOptions)
