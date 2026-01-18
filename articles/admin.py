"""
Admin configuration for articles app with multilingual support.
"""
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from .models import Article


@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    """
    Admin interface for Article model with multilingual support.
    Title and content fields will be shown as tabs for each language.
    """

    list_display = (
        'title',
        'author',
        'status',
        'views',
        'cover_image_preview',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'status',
        'created_at',
        'updated_at',
        'author'
    )

    search_fields = (
        'title',
        'title_uz',
        'title_ru',
        'title_en',
        'content',
        'author__username',
        'author__email'
    )

    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = (
        'slug',
        'views',
        'created_at',
        'updated_at',
        'cover_image_preview'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Media', {
            'fields': ('cover_image', 'cover_image_preview', 'article_file')
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Ordering
    ordering = ('-created_at',)

    # Items per page
    list_per_page = 25

    # Date hierarchy for easy filtering
    date_hierarchy = 'created_at'

    # Actions
    actions = ['make_published', 'make_draft', 'reset_views']

    def cover_image_preview(self, obj):
        """Display cover image thumbnail in admin."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="150" height="auto" style="border-radius: 5px;" />',
                obj.cover_image.url
            )
        return "No image"

    cover_image_preview.short_description = "Cover Preview"

    def make_published(self, request, queryset):
        """Bulk action to publish articles."""
        updated = queryset.update(status=Article.ArticleStatus.PUBLISHED)
        self.message_user(request, f'{updated} article(s) published.')

    make_published.short_description = "Publish selected articles"

    def make_draft(self, request, queryset):
        """Bulk action to convert articles to draft."""
        updated = queryset.update(status=Article.ArticleStatus.DRAFT)
        self.message_user(request, f'{updated} article(s) converted to draft.')

    make_draft.short_description = "Convert to draft"

    def reset_views(self, request, queryset):
        """Reset view counter for selected articles."""
        updated = queryset.update(views=0)
        self.message_user(request, f'View counter reset for {updated} article(s).')

    reset_views.short_description = "Reset view counter"

    def save_model(self, request, obj, form, change):
        """Auto-set author if creating new article."""
        if not change:  # Creating new article
            if not obj.author_id:
                obj.author = request.user
        super().save_model(request, obj, form, change)

    # Enable tabbed translation interface
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }
