"""
Admin configuration for users app with editorial workflow support.
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ArticleRules, Notification


class CustomUserChangeForm(forms.ModelForm):
    """Custom form that adds assigned_categories reverse M2M field."""

    assigned_categories = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(_('Categories'), is_stacked=False),
        label=_('Assigned Categories'),
        help_text=_('Categories this reviewer can review. Only applies to users with Reviewer role.'),
    )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from articles.models import Category
        self.fields['assigned_categories'].queryset = Category.objects.filter(is_active=True)
        if self.instance.pk:
            self.fields['assigned_categories'].initial = self.instance.assigned_categories.all()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.assigned_categories.set(self.cleaned_data['assigned_categories'])
        else:
            # save_m2m will be called later by the admin
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                user.assigned_categories.set(self.cleaned_data['assigned_categories'])
            self.save_m2m = new_save_m2m
        return user


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for CustomUser model with role management.
    """

    form = CustomUserChangeForm

    list_display = (
        'username',
        'email',
        'role',
        'assigned_categories_display',
        'organization',
        'is_staff',
        'is_active',
        'date_joined'
    )

    list_filter = (
        'role',
        'is_staff',
        'is_active',
        'date_joined'
    )

    search_fields = ('username', 'email', 'first_name', 'last_name', 'organization')

    fieldsets = UserAdmin.fieldsets + (
        (_('Role & Profile'), {
            'fields': ('role', 'bio', 'organization')
        }),
        (_('Reviewer Categories'), {
            'fields': ('assigned_categories',),
            'description': _('Assign categories for reviewers. Only relevant for users with Reviewer role.'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Additional Info'), {
            'fields': ('email', 'role', 'organization')
        }),
    )

    list_per_page = 25
    date_hierarchy = 'date_joined'

    actions = ['make_author', 'make_reader', 'make_reviewer_with_notification', 'make_admin']

    def assigned_categories_display(self, obj):
        """Display assigned categories for reviewers."""
        if obj.role == CustomUser.UserRole.REVIEWER:
            categories = obj.assigned_categories.all()[:3]
            if categories:
                names = [c.name_uz for c in categories]
                total = obj.assigned_categories.count()
                if total > 3:
                    names.append(f'... (+{total - 3})')
                return ', '.join(names)
        return '-'
    assigned_categories_display.short_description = _('Assigned Categories')

    def save_model(self, request, obj, form, change):
        """Track role changes and send notifications."""
        if change:
            old_obj = CustomUser.objects.get(pk=obj.pk)
            old_role = old_obj.role
        else:
            old_role = None

        super().save_model(request, obj, form, change)

        # Check if user was promoted to reviewer
        if old_role != CustomUser.UserRole.REVIEWER and obj.role == CustomUser.UserRole.REVIEWER:
            self._notify_reviewer_assigned(obj, request.user)

    def _notify_reviewer_assigned(self, user, assigned_by):
        """Send notification when user is assigned as reviewer."""
        from .services import notify_reviewer_assigned
        categories = list(user.assigned_categories.all())
        notify_reviewer_assigned(user, categories, assigned_by)

    @admin.action(description=_("Change selected users to Author"))
    def make_author(self, request, queryset):
        """Bulk action to make users authors."""
        updated = queryset.update(role=CustomUser.UserRole.AUTHOR)
        self.message_user(request, f'{updated} user(s) changed to Author role.')

    @admin.action(description=_("Change selected users to Reader"))
    def make_reader(self, request, queryset):
        """Bulk action to make users readers."""
        updated = queryset.update(role=CustomUser.UserRole.READER)
        self.message_user(request, f'{updated} user(s) changed to Reader role.')

    @admin.action(description=_("Make Reviewer and Send Notification"))
    def make_reviewer_with_notification(self, request, queryset):
        """Bulk action to make users reviewers with email notification."""
        from .services import notify_reviewer_assigned

        count = 0
        for user in queryset:
            if user.role != CustomUser.UserRole.REVIEWER:
                user.role = CustomUser.UserRole.REVIEWER
                user.save()
                categories = list(user.assigned_categories.all())
                notify_reviewer_assigned(user, categories, request.user)
                count += 1

        self.message_user(
            request,
            f'{count} user(s) changed to Reviewer role and notified.'
        )

    @admin.action(description=_("Change selected users to Admin"))
    def make_admin(self, request, queryset):
        """Bulk action to make users admins."""
        updated = queryset.update(role=CustomUser.UserRole.ADMIN)
        self.message_user(request, f'{updated} user(s) changed to Admin role.')


@admin.register(ArticleRules)
class ArticleRulesAdmin(admin.ModelAdmin):
    """
    Admin for Article Rules model.
    """

    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'rules_file', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """Ensure only one active rules set."""
        if obj.is_active:
            ArticleRules.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin for Notification model.
    """

    list_display = (
        'user',
        'notification_type_badge',
        'title',
        'is_read',
        'created_at',
    )

    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        (None, {
            'fields': ('user', 'notification_type', 'title', 'message', 'link', 'is_read')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def notification_type_badge(self, obj):
        """Display notification type as a colored badge."""
        colors = {
            'REVIEWER_ASSIGNED': '#17a2b8',
            'ARTICLE_FOR_REVIEW': '#fd7e14',
            'REVIEW_SUBMITTED': '#6f42c1',
            'ARTICLE_PUBLISHED': '#28a745',
            'ARTICLE_REJECTED': '#dc3545',
            'CHANGES_REQUESTED': '#ffc107',
            'STATUS_CHANGED': '#6c757d',
            'GENERAL': '#007bff',
        }
        color = colors.get(obj.notification_type, '#6c757d')
        text_color = 'white' if obj.notification_type != 'CHANGES_REQUESTED' else 'black'
        return format_html(
            '<span style="background-color: {}; color: {}; '
            'padding: 2px 8px; border-radius: 4px; font-size: 0.85em;">'
            '{}</span>',
            color,
            text_color,
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = _('Type')

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description=_("Mark selected as read"))
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')

    @admin.action(description=_("Mark selected as unread"))
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
