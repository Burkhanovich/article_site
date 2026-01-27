"""
Translation configuration for articles app.

Note: The Article and Category models in this app use explicit multilingual fields
(e.g., title_uz, title_ru, title_en) instead of django-modeltranslation.
This approach provides more control over field definitions and doesn't require
modeltranslation to manage the translations.

This file is kept for compatibility but doesn't register any models.
"""
# No model registrations needed - multilingual fields are defined directly in models
