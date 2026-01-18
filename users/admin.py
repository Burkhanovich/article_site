"""
Admin configuration for users app with multilingual support.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from modeltranslation.admin import TranslationAdmin
from .models import CustomUser, ArticleRules


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for CustomUser model.
    """

    list_display = (
        'username',
        'email',
        'role',
        'has_accepted_rules',
        'is_staff',
        'is_active',
        'date_joined'
    )

    list_filter = (
        'role',
        'has_accepted_rules',
        'is_staff',
        'is_active',
        'date_joined'
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role', 'has_accepted_rules')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')

    # Fields shown when adding new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'role')
        }),
    )

    # Enable filtering in right sidebar
    list_per_page = 25
    date_hierarchy = 'date_joined'

    actions = ['make_author', 'make_reader', 'reset_rules_acceptance']

    def make_author(self, request, queryset):
        """Bulk action to make users authors."""
        updated = queryset.update(role=CustomUser.UserRole.AUTHOR)
        self.message_user(request, f'{updated} user(s) changed to Author role.')

    make_author.short_description = "Change selected users to Author"

    def make_reader(self, request, queryset):
        """Bulk action to make users readers."""
        updated = queryset.update(
            role=CustomUser.UserRole.READER,
            has_accepted_rules=False
        )
        self.message_user(request, f'{updated} user(s) changed to Reader role.')

    make_reader.short_description = "Change selected users to Reader"

    def reset_rules_acceptance(self, request, queryset):
        """Reset rules acceptance for selected users."""
        updated = queryset.update(has_accepted_rules=False)
        self.message_user(request, f'Rules acceptance reset for {updated} user(s).')

    reset_rules_acceptance.short_description = "Reset rules acceptance"


@admin.register(ArticleRules)
class ArticleRulesAdmin(TranslationAdmin):
    """
    Admin for Article Rules model with multilingual support.
    Fields will be shown as tabs for each language (Uzbek, Russian, English).
    """

    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'title_uz', 'title_ru', 'title_en', 'content')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'rules_file', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    # Group multilingual fields
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

    # Only allow one active rules set
    def save_model(self, request, obj, form, change):
        """Ensure only one active rules set."""
        if obj.is_active:
            ArticleRules.objects.filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)
