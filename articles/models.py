"""
Article models for the editorial publishing platform.
Includes Category, CategoryPolicy, Article, Keyword, Review, and ArticleStatusHistory.
"""
import os
from django.conf import settings
from django.db import models
from django.db.models import Count, Q
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Category(models.Model):
    """
    Category model with multilingual names and reviewer assignments.
    """
    name_uz = models.CharField(max_length=100, verbose_name=_('Name (Uzbek)'))
    name_ru = models.CharField(max_length=100, verbose_name=_('Name (Russian)'))
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))

    slug = models.SlugField(max_length=120, unique=True, verbose_name=_('Slug'))

    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))

    reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_categories',
        blank=True,
        verbose_name=_('Assigned Reviewers'),
        help_text=_('Reviewers who can review articles in this category'),
        limit_choices_to={'role': 'REVIEWER'}
    )

    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name_uz']

    def __str__(self):
        return self.name_uz

    def get_name(self, lang='uz'):
        """Get category name in specified language."""
        return getattr(self, f'name_{lang}', self.name_uz)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_uz)
        super().save(*args, **kwargs)


class CategoryPolicy(models.Model):
    """
    Per-category workflow policy for article review.
    """
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='policy',
        verbose_name=_('Category')
    )

    min_approvals_to_publish = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Minimum Approvals to Publish'),
        help_text=_('Number of approval votes required')
    )

    max_rejections_before_block = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Maximum Rejections Before Block'),
        help_text=_('Article is blocked if rejections exceed this')
    )

    min_required_reviews = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Minimum Required Reviews'),
        help_text=_('Total reviews needed before decision')
    )

    allow_admin_override = models.BooleanField(
        default=True,
        verbose_name=_('Allow Admin Override'),
        help_text=_('Admin can override policy and publish/reject directly')
    )

    review_deadline_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Review Deadline (Hours)'),
        help_text=_('Optional deadline for reviews')
    )

    require_changes_comment = models.BooleanField(
        default=True,
        verbose_name=_('Require Comment for Changes'),
        help_text=_('Reviewer must provide comment when requesting changes')
    )

    require_reject_comment = models.BooleanField(
        default=True,
        verbose_name=_('Require Comment for Rejection'),
        help_text=_('Reviewer must provide comment when rejecting')
    )

    class Meta:
        verbose_name = _('Category Policy')
        verbose_name_plural = _('Category Policies')

    def __str__(self):
        return f"Policy: {self.category.name_uz}"


class Keyword(models.Model):
    """
    Normalized keyword model for articles.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Keyword')
    )
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower().strip()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_from_string(cls, keywords_string):
        """
        Parse comma-separated keywords and return list of Keyword objects.
        Creates new keywords if they don't exist.
        """
        keywords = []
        if not keywords_string:
            return keywords

        for kw in keywords_string.split(','):
            kw = kw.strip().lower()
            if kw:
                keyword, _ = cls.objects.get_or_create(
                    name=kw,
                    defaults={'slug': slugify(kw)}
                )
                keywords.append(keyword)
        return keywords


class Article(models.Model):
    """
    Article model with full editorial workflow support.
    """

    class ArticleStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING_ADMIN = 'PENDING_ADMIN', _('Pending Admin Review')
        IN_REVIEW = 'IN_REVIEW', _('In Review')
        CHANGES_REQUESTED = 'CHANGES_REQUESTED', _('Changes Requested')
        REJECTED = 'REJECTED', _('Rejected')
        PUBLISHED = 'PUBLISHED', _('Published')

    class ReviewMode(models.TextChoices):
        ALL_CATEGORIES = 'ALL', _('All Categories Required')
        ANY_CATEGORY = 'ANY', _('Any Category Sufficient')

    # Multilingual title
    title_uz = models.CharField(max_length=300, verbose_name=_('Title (Uzbek)'))
    title_ru = models.CharField(max_length=300, blank=True, verbose_name=_('Title (Russian)'))
    title_en = models.CharField(max_length=300, blank=True, verbose_name=_('Title (English)'))

    slug = models.SlugField(max_length=350, unique=True, blank=True)

    # Multilingual content
    content_uz = models.TextField(verbose_name=_('Content (Uzbek)'))
    content_ru = models.TextField(blank=True, verbose_name=_('Content (Russian)'))
    content_en = models.TextField(blank=True, verbose_name=_('Content (English)'))

    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('Author')
    )

    # Categories (M2M - article can belong to multiple categories)
    categories = models.ManyToManyField(
        Category,
        related_name='articles',
        verbose_name=_('Categories'),
        help_text=_('Select at least one category')
    )

    # Keywords
    keywords = models.ManyToManyField(
        Keyword,
        related_name='articles',
        blank=True,
        verbose_name=_('Keywords')
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        verbose_name=_('Status')
    )

    # Review mode for multi-category articles
    review_mode = models.CharField(
        max_length=10,
        choices=ReviewMode.choices,
        default=ReviewMode.ALL_CATEGORIES,
        verbose_name=_('Review Mode'),
        help_text=_('How multi-category reviews are evaluated')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Submitted At'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Published At'))

    # Admin decision tracking
    admin_decision_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_decisions',
        verbose_name=_('Admin Decision By')
    )
    admin_decision_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Admin Decision At'))
    admin_note = models.TextField(blank=True, null=True, verbose_name=_('Admin Note'))

    # Article file upload
    article_file = models.FileField(
        upload_to='article_files/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Article File'),
        help_text=_('Upload article file (PDF, DOC, DOCX). Max 20MB.')
    )

    # View counter
    views = models.PositiveIntegerField(default=0, verbose_name=_('Views'))

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title_uz

    @property
    def title(self):
        """Return the primary title (Uzbek)."""
        return self.title_uz

    @property
    def content(self):
        """Return the primary content (Uzbek)."""
        return self.content_uz

    def get_title(self, lang='uz'):
        """Get title in specified language with fallback."""
        title = getattr(self, f'title_{lang}', None)
        return title if title else self.title_uz

    def get_content(self, lang='uz'):
        """Get content in specified language with fallback."""
        content = getattr(self, f'content_{lang}', None)
        return content if content else self.content_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.title_uz)[:300]
        unique_slug = base_slug
        counter = 1
        while Article.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f'{base_slug}-{counter}'
            counter += 1
        return unique_slug

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    # Status properties
    @property
    def is_draft(self):
        return self.status == self.ArticleStatus.DRAFT

    @property
    def is_pending_admin(self):
        return self.status == self.ArticleStatus.PENDING_ADMIN

    @property
    def is_in_review(self):
        return self.status == self.ArticleStatus.IN_REVIEW

    @property
    def is_changes_requested(self):
        return self.status == self.ArticleStatus.CHANGES_REQUESTED

    @property
    def is_rejected(self):
        return self.status == self.ArticleStatus.REJECTED

    @property
    def is_published(self):
        return self.status == self.ArticleStatus.PUBLISHED

    @property
    def can_be_edited_by_author(self):
        """Author can edit DRAFT and CHANGES_REQUESTED articles."""
        return self.status in [self.ArticleStatus.DRAFT, self.ArticleStatus.CHANGES_REQUESTED]

    @property
    def can_be_reviewed(self):
        """Reviewers can review IN_REVIEW and CHANGES_REQUESTED articles."""
        return self.status in [self.ArticleStatus.IN_REVIEW, self.ArticleStatus.CHANGES_REQUESTED]

    @property
    def can_be_submitted(self):
        """Author can submit DRAFT or CHANGES_REQUESTED articles for review."""
        return self.status in [self.ArticleStatus.DRAFT, self.ArticleStatus.CHANGES_REQUESTED]

    @property
    def is_pending_review(self):
        """Check if article is pending admin review."""
        return self.status == self.ArticleStatus.PENDING_ADMIN

    @property
    def rejection_reason(self):
        """Alias for admin_note when article is rejected."""
        return self.admin_note if self.is_rejected else None

    @property
    def reviewed_at(self):
        """Alias for admin_decision_at."""
        return self.admin_decision_at

    @property
    def reviewed_by(self):
        """Alias for admin_decision_by."""
        return self.admin_decision_by

    def get_file_extension(self):
        """Return file extension."""
        if self.article_file:
            return os.path.splitext(self.article_file.name)[1].lstrip('.').upper()
        return ''

    def get_file_size(self):
        """Return file size in MB."""
        if self.article_file:
            try:
                return round(self.article_file.size / (1024 * 1024), 2)
            except Exception:
                return 0
        return 0

    def get_keywords_string(self):
        """Return comma-separated keywords string."""
        return ', '.join(kw.name for kw in self.keywords.all())

    def set_keywords_from_string(self, keywords_string):
        """Set keywords from comma-separated string."""
        keywords = Keyword.get_or_create_from_string(keywords_string)
        self.keywords.set(keywords)

    # Workflow methods
    def submit_to_admin(self):
        """Author submits article to admin for triage."""
        if self.status in [self.ArticleStatus.DRAFT, self.ArticleStatus.CHANGES_REQUESTED]:
            old_status = self.status
            self.status = self.ArticleStatus.PENDING_ADMIN
            self.submitted_at = timezone.now()
            self.save()
            self._log_status_change(old_status, self.status, self.author, 'Author submitted')
            return True
        return False

    def send_to_review(self, admin_user, note=None):
        """Admin sends article to reviewers."""
        if self.status == self.ArticleStatus.PENDING_ADMIN:
            old_status = self.status
            self.status = self.ArticleStatus.IN_REVIEW
            self.admin_note = note
            self.save()
            self._log_status_change(old_status, self.status, admin_user, 'Sent to review')
            return True
        return False

    def request_changes(self, admin_user, note=None):
        """Admin or system requests changes from author."""
        old_status = self.status
        self.status = self.ArticleStatus.CHANGES_REQUESTED
        self.admin_note = note
        self.save()
        self._log_status_change(old_status, self.status, admin_user, note or 'Changes requested')
        return True

    def reject(self, admin_user, note=None):
        """Admin rejects article."""
        old_status = self.status
        self.status = self.ArticleStatus.REJECTED
        self.admin_decision_by = admin_user
        self.admin_decision_at = timezone.now()
        self.admin_note = note
        self.save()
        self._log_status_change(old_status, self.status, admin_user, note or 'Rejected')
        return True

    def publish(self, admin_user, note=None):
        """Admin publishes article."""
        old_status = self.status
        self.status = self.ArticleStatus.PUBLISHED
        self.admin_decision_by = admin_user
        self.admin_decision_at = timezone.now()
        self.published_at = timezone.now()
        self.admin_note = note
        self.save()
        self._log_status_change(old_status, self.status, admin_user, note or 'Published')
        return True

    def _log_status_change(self, from_status, to_status, user, reason=''):
        """Log status change to history."""
        ArticleStatusHistory.objects.create(
            article=self,
            from_status=from_status,
            to_status=to_status,
            changed_by=user,
            reason=reason
        )


class Review(models.Model):
    """
    Review model for per-category article reviews.
    """

    class Decision(models.TextChoices):
        APPROVE = 'APPROVE', _('Approve')
        CHANGES = 'CHANGES', _('Request Changes')
        REJECT = 'REJECT', _('Reject')

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Article')
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Reviewer')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Category'),
        help_text=_('The category this review is for')
    )

    decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        verbose_name=_('Decision')
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Comment')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        # One active review per reviewer per article per category
        unique_together = ['article', 'reviewer', 'category']

    def __str__(self):
        return f"{self.reviewer.username} - {self.article.title_uz[:30]} ({self.category.name_uz})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check reviewer is assigned to category
        if not self.category.reviewers.filter(pk=self.reviewer.pk).exists():
            if not self.reviewer.is_superuser:
                raise ValidationError(_('You are not assigned to review this category.'))

        # Check article has this category
        if not self.article.categories.filter(pk=self.category.pk).exists():
            raise ValidationError(_('Article does not belong to this category.'))

        # Check article is reviewable
        if not self.article.can_be_reviewed:
            raise ValidationError(_('This article cannot be reviewed in its current status.'))

        # Check comment requirements
        policy = getattr(self.category, 'policy', None)
        if policy:
            if self.decision == self.Decision.CHANGES and policy.require_changes_comment:
                if not self.comment:
                    raise ValidationError(_('Comment is required when requesting changes.'))
            if self.decision == self.Decision.REJECT and policy.require_reject_comment:
                if not self.comment:
                    raise ValidationError(_('Comment is required when rejecting.'))


class ReviewerAssignment(models.Model):
    """
    Model to track reviewer assignments to specific articles.
    This allows admin to assign specific reviewers to articles,
    independent of category-based reviewer assignments.
    """

    class AssignmentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Review')
        APPROVED = 'APPROVED', _('Approved')
        CHANGES_REQUESTED = 'CHANGES_REQUESTED', _('Changes Requested')
        REJECTED = 'REJECTED', _('Rejected')

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='reviewer_assignments',
        verbose_name=_('Article')
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_assignments',
        verbose_name=_('Reviewer'),
        limit_choices_to={'role': 'REVIEWER'}
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewer_assignments_made',
        verbose_name=_('Assigned By')
    )

    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.PENDING,
        verbose_name=_('Status')
    )

    review_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Review Comment'),
        help_text=_('Reviewer feedback or comment')
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Assigned At')
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Reviewer Assignment')
        verbose_name_plural = _('Reviewer Assignments')
        ordering = ['-assigned_at']
        # One assignment per reviewer per article
        unique_together = ['article', 'reviewer']
        indexes = [
            models.Index(fields=['article', 'status']),
            models.Index(fields=['reviewer', 'status']),
        ]

    def __str__(self):
        return f"{self.reviewer.username} -> {self.article.title_uz[:30]} ({self.get_status_display()})"

    def mark_approved(self, comment=None):
        """Mark the assignment as approved."""
        self.status = self.AssignmentStatus.APPROVED
        if comment:
            self.review_comment = comment
        self.reviewed_at = timezone.now()
        self.save()

    def mark_changes_requested(self, comment):
        """Mark the assignment as changes requested."""
        self.status = self.AssignmentStatus.CHANGES_REQUESTED
        self.review_comment = comment
        self.reviewed_at = timezone.now()
        self.save()

    def mark_rejected(self, comment=None):
        """Mark the assignment as rejected."""
        self.status = self.AssignmentStatus.REJECTED
        if comment:
            self.review_comment = comment
        self.reviewed_at = timezone.now()
        self.save()

    def reset_to_pending(self):
        """Reset assignment to pending (e.g., when author resubmits)."""
        self.status = self.AssignmentStatus.PENDING
        self.reviewed_at = None
        self.save()


class ArticleStatusHistory(models.Model):
    """
    Audit log for article status changes.
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Article')
    )

    from_status = models.CharField(
        max_length=20,
        choices=Article.ArticleStatus.choices,
        verbose_name=_('From Status')
    )

    to_status = models.CharField(
        max_length=20,
        choices=Article.ArticleStatus.choices,
        verbose_name=_('To Status')
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Changed By')
    )

    reason = models.TextField(blank=True, verbose_name=_('Reason'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Article Status History')
        verbose_name_plural = _('Article Status Histories')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.article.title_uz[:30]}: {self.from_status} → {self.to_status}"
