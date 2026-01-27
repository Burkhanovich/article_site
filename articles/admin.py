"""
Admin configuration for articles app with editorial workflow and multilingual support.
"""
from django.contrib import admin
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Category, CategoryPolicy, Keyword, Article, Review, ArticleStatusHistory
from .services import is_article_publishable


class CategoryPolicyInline(admin.StackedInline):
    """Inline for CategoryPolicy on Category admin."""
    model = CategoryPolicy
    can_delete = False
    verbose_name_plural = _('Category Policy')
    fieldsets = (
        (_('Approval Requirements'), {
            'fields': (
                'min_approvals_to_publish',
                'max_rejections_before_block',
                'min_required_reviews',
            )
        }),
        (_('Options'), {
            'fields': (
                'allow_admin_override',
                'review_deadline_hours',
                'require_changes_comment',
                'require_reject_comment',
            )
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    list_display = (
        'name_uz',
        'name_ru',
        'name_en',
        'slug',
        'reviewer_count',
        'article_count',
        'is_active',
    )
    list_filter = ('is_active',)
    search_fields = ('name_uz', 'name_ru', 'name_en', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    filter_horizontal = ('reviewers',)
    inlines = [CategoryPolicyInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Names (Multilingual)'), {
            'fields': ('name_uz', 'name_ru', 'name_en', 'slug')
        }),
        (_('Details'), {
            'fields': ('description', 'is_active')
        }),
        (_('Reviewers'), {
            'fields': ('reviewers',),
            'description': _('Assign reviewers who can review articles in this category')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def reviewer_count(self, obj):
        count = obj.reviewers.count()
        return format_html('<span style="font-weight:bold;">{}</span>', count)
    reviewer_count.short_description = _('Reviewers')

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _('Articles')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('reviewers', 'articles')


@admin.register(CategoryPolicy)
class CategoryPolicyAdmin(admin.ModelAdmin):
    """Standalone admin for CategoryPolicy (for overview/bulk edits)."""
    list_display = (
        'category',
        'min_approvals_to_publish',
        'max_rejections_before_block',
        'min_required_reviews',
        'allow_admin_override',
    )
    list_filter = ('allow_admin_override', 'require_changes_comment', 'require_reject_comment')
    search_fields = ('category__name_uz', 'category__name_ru', 'category__name_en')
    list_editable = ('min_approvals_to_publish', 'max_rejections_before_block', 'min_required_reviews')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    """Admin for Keyword model."""
    list_display = ('name', 'slug', 'article_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _('Articles')


class StatusFilter(admin.SimpleListFilter):
    """Custom filter for article status with translated labels."""
    title = _('Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Article.ArticleStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class PublishabilityFilter(admin.SimpleListFilter):
    """Filter for publishable articles."""
    title = _('Publishability')
    parameter_name = 'publishable'

    def lookups(self, request, model_admin):
        return (
            ('ready', _('Ready to Publish')),
            ('blocked', _('Blocked')),
            ('in_progress', _('Review In Progress')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        result_ids = []
        for article in queryset.filter(status__in=['IN_REVIEW', 'CHANGES_REQUESTED']):
            publishability = is_article_publishable(article)
            if self.value() == 'ready' and publishability.is_publishable:
                result_ids.append(article.id)
            elif self.value() == 'blocked' and any(s.is_blocked for s in publishability.category_statuses):
                result_ids.append(article.id)
            elif self.value() == 'in_progress' and not publishability.is_publishable:
                if not any(s.is_blocked for s in publishability.category_statuses):
                    result_ids.append(article.id)

        return queryset.filter(id__in=result_ids)


class ReviewInline(admin.TabularInline):
    """Inline for reviews on Article admin."""
    model = Review
    extra = 0
    readonly_fields = ('reviewer', 'category', 'decision', 'comment', 'created_at')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class StatusHistoryInline(admin.TabularInline):
    """Inline for status history on Article admin."""
    model = ArticleStatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'reason', 'timestamp')
    can_delete = False
    ordering = ('-timestamp',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model with editorial workflow."""

    list_display = (
        'title_uz',
        'author',
        'status_badge',
        'publishability_badge',
        'category_list',
        'review_count',
        'submitted_at',
        'views',
        'created_at',
    )

    list_filter = (
        StatusFilter,
        PublishabilityFilter,
        'categories',
        'author',
        'review_mode',
        'created_at',
        'submitted_at',
    )

    search_fields = (
        'title_uz',
        'title_ru',
        'title_en',
        'content_uz',
        'author__username',
        'author__email',
        'keywords__name',
    )

    readonly_fields = (
        'slug',
        'views',
        'created_at',
        'updated_at',
        'submitted_at',
        'published_at',
        'admin_decision_by',
        'admin_decision_at',
        'publishability_info',
    )

    filter_horizontal = ('categories', 'keywords')

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title_uz', 'title_ru', 'title_en', 'slug', 'author', 'status')
        }),
        (_('Content'), {
            'fields': ('content_uz', 'content_ru', 'content_en')
        }),
        (_('Classification'), {
            'fields': ('categories', 'keywords', 'review_mode')
        }),
        (_('Publishing Status'), {
            'fields': ('publishability_info',),
            'classes': ('wide',),
        }),
        (_('Admin Decision'), {
            'fields': ('admin_note', 'admin_decision_by', 'admin_decision_at'),
            'classes': ('collapse',),
        }),
        (_('Statistics'), {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ReviewInline, StatusHistoryInline]
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['send_to_review', 'request_changes', 'publish_articles', 'reject_articles', 'reset_to_draft']

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'DRAFT': '#6c757d',
            'PENDING_ADMIN': '#fd7e14',
            'IN_REVIEW': '#17a2b8',
            'CHANGES_REQUESTED': '#ffc107',
            'PUBLISHED': '#28a745',
            'REJECTED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-size: 0.85em;">'
            '{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def publishability_badge(self, obj):
        """Display publishability status."""
        if obj.status not in ['IN_REVIEW', 'CHANGES_REQUESTED']:
            return '-'

        publishability = is_article_publishable(obj)

        if publishability.is_publishable:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">'
                'Ready</span>'
            )
        elif any(s.is_blocked for s in publishability.category_statuses):
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">'
                'Blocked</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; '
                'padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">'
                'In Progress</span>'
            )
    publishability_badge.short_description = _('Publishable')

    def category_list(self, obj):
        """Display categories as a comma-separated list."""
        categories = obj.categories.all()[:3]
        names = [c.name_uz for c in categories]
        if obj.categories.count() > 3:
            names.append('...')
        return ', '.join(names) if names else '-'
    category_list.short_description = _('Categories')

    def review_count(self, obj):
        """Display review count."""
        count = obj.reviews.count()
        approvals = obj.reviews.filter(decision='APPROVE').count()
        if count == 0:
            return '-'
        return format_html('{} <small>({})</small>', count, approvals)
    review_count.short_description = _('Reviews')

    def publishability_info(self, obj):
        """Display detailed publishability information."""
        if obj.status not in ['IN_REVIEW', 'CHANGES_REQUESTED', 'PENDING_ADMIN']:
            return _('N/A - Article is not in review')

        publishability = is_article_publishable(obj)
        html = f'<strong>{publishability.overall_message}</strong><br><br>'

        html += '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background:#f5f5f5;"><th style="padding:5px; text-align:left;">Category</th>'
        html += '<th style="padding:5px;">Reviews</th><th style="padding:5px;">Approvals</th>'
        html += '<th style="padding:5px;">Rejections</th><th style="padding:5px;">Status</th></tr>'

        for status in publishability.category_statuses:
            row_color = '#d4edda' if status.meets_policy else ('#f8d7da' if status.is_blocked else '#fff3cd')
            html += f'<tr style="background:{row_color};">'
            html += f'<td style="padding:5px;">{status.category.name_uz}</td>'
            html += f'<td style="padding:5px; text-align:center;">{status.total_reviews}</td>'
            html += f'<td style="padding:5px; text-align:center;">{status.approvals}</td>'
            html += f'<td style="padding:5px; text-align:center;">{status.rejections}</td>'
            html += f'<td style="padding:5px;">{status.policy_message}</td>'
            html += '</tr>'

        html += '</table>'
        return format_html(html)
    publishability_info.short_description = _('Review Status by Category')

    @admin.action(description=_("Send to Review (from Pending Admin)"))
    def send_to_review(self, request, queryset):
        """Send pending articles to review and notify reviewers."""
        from users.services import notify_reviewers_for_article

        pending = queryset.filter(status=Article.ArticleStatus.PENDING_ADMIN)
        count = 0
        reviewers_notified = 0
        for article in pending:
            if article.send_to_review(request.user, note='Sent to review by admin'):
                count += 1
                # Notify all eligible reviewers
                reviewers_notified += notify_reviewers_for_article(article, request.user)

        if count:
            self.message_user(
                request,
                _("%(count)d article(s) sent to review. %(reviewers)d reviewer(s) notified.") % {
                    'count': count,
                    'reviewers': reviewers_notified
                },
                messages.SUCCESS
            )
        else:
            self.message_user(request, _("No pending articles selected."), messages.WARNING)

    @admin.action(description=_("Request Changes from Author"))
    def request_changes(self, request, queryset):
        """Request changes from author and send notification."""
        from users.services import notify_changes_requested

        reviewable = queryset.filter(status__in=[Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.PENDING_ADMIN])
        count = 0
        for article in reviewable:
            if article.request_changes(request.user, note='Changes requested by admin'):
                count += 1
                # Notify author
                notify_changes_requested(article.author, article, article.admin_note)

        if count:
            self.message_user(request, _("Changes requested for %(count)d article(s).") % {'count': count}, messages.SUCCESS)
        else:
            self.message_user(request, _("No eligible articles selected."), messages.WARNING)

    @admin.action(description=_("Publish Articles"))
    def publish_articles(self, request, queryset):
        """Publish articles and notify authors."""
        from users.services import notify_article_published

        count = 0
        for article in queryset:
            if article.status in [Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.PENDING_ADMIN]:
                if article.publish(request.user, note='Published by admin'):
                    count += 1
                    # Notify author
                    notify_article_published(article.author, article)

        if count:
            self.message_user(request, _("%(count)d article(s) published.") % {'count': count}, messages.SUCCESS)
        else:
            self.message_user(request, _("No eligible articles selected."), messages.WARNING)

    @admin.action(description=_("Reject Articles"))
    def reject_articles(self, request, queryset):
        """Reject articles and notify authors."""
        from users.services import notify_article_rejected

        count = 0
        for article in queryset:
            if article.status in [Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.PENDING_ADMIN]:
                if article.reject(request.user, note='Rejected by admin'):
                    count += 1
                    # Notify author
                    notify_article_rejected(article.author, article, article.admin_note, request.user)

        if count:
            self.message_user(request, _("%(count)d article(s) rejected.") % {'count': count}, messages.SUCCESS)
        else:
            self.message_user(request, _("No eligible articles selected."), messages.WARNING)

    @admin.action(description=_("Reset to Draft"))
    def reset_to_draft(self, request, queryset):
        """Reset articles to draft status."""
        count = 0
        for article in queryset:
            old_status = article.status
            article.status = Article.ArticleStatus.DRAFT
            article.submitted_at = None
            article.admin_note = None
            article.admin_decision_by = None
            article.admin_decision_at = None
            article.save()
            article._log_status_change(old_status, Article.ArticleStatus.DRAFT, request.user, 'Reset to draft by admin')
            count += 1

        self.message_user(request, _("%(count)d article(s) reset to draft.") % {'count': count}, messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        """Handle status changes and auto-set author."""
        if not change and not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'author', 'admin_decision_by'
        ).prefetch_related('categories', 'keywords', 'reviews')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    list_display = (
        'article_title',
        'reviewer',
        'category',
        'decision_badge',
        'has_comment',
        'created_at',
    )
    list_filter = ('decision', 'category', 'reviewer', 'created_at')
    search_fields = (
        'article__title_uz',
        'article__title_ru',
        'reviewer__username',
        'category__name_uz',
        'comment',
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('article', 'reviewer')

    fieldsets = (
        (_('Review Details'), {
            'fields': ('article', 'reviewer', 'category', 'decision', 'comment')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def article_title(self, obj):
        return obj.article.title_uz[:50]
    article_title.short_description = _('Article')

    def decision_badge(self, obj):
        """Display decision as a colored badge."""
        colors = {
            'APPROVE': '#28a745',
            'CHANGES': '#ffc107',
            'REJECT': '#dc3545',
        }
        text_colors = {
            'APPROVE': 'white',
            'CHANGES': 'black',
            'REJECT': 'white',
        }
        color = colors.get(obj.decision, '#6c757d')
        text_color = text_colors.get(obj.decision, 'white')
        return format_html(
            '<span style="background-color: {}; color: {}; '
            'padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">'
            '{}</span>',
            color,
            text_color,
            obj.get_decision_display()
        )
    decision_badge.short_description = _('Decision')
    decision_badge.admin_order_field = 'decision'

    def has_comment(self, obj):
        return bool(obj.comment)
    has_comment.short_description = _('Comment')
    has_comment.boolean = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'reviewer', 'category')


@admin.register(ArticleStatusHistory)
class ArticleStatusHistoryAdmin(admin.ModelAdmin):
    """Admin for ArticleStatusHistory model (read-only audit log)."""
    list_display = (
        'article_title',
        'status_change',
        'changed_by',
        'reason_preview',
        'timestamp',
    )
    list_filter = ('from_status', 'to_status', 'changed_by', 'timestamp')
    search_fields = ('article__title_uz', 'changed_by__username', 'reason')
    readonly_fields = ('article', 'from_status', 'to_status', 'changed_by', 'reason', 'timestamp')
    date_hierarchy = 'timestamp'

    def article_title(self, obj):
        return obj.article.title_uz[:50]
    article_title.short_description = _('Article')

    def status_change(self, obj):
        return format_html(
            '{} &rarr; {}',
            obj.get_from_status_display(),
            obj.get_to_status_display()
        )
    status_change.short_description = _('Status Change')

    def reason_preview(self, obj):
        if obj.reason:
            return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
        return '-'
    reason_preview.short_description = _('Reason')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'changed_by')
