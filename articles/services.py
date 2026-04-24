"""
Service layer for article publishing platform.
Contains business logic for policy-based review eligibility and publishing decisions.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _

from .models import Article, Category, CategoryPolicy, Review


@dataclass
class CategoryReviewStatus:
    """Status of reviews for a single category."""
    category: Category
    total_reviews: int
    approvals: int
    rejections: int
    changes_requested: int
    meets_policy: bool
    policy_message: str
    is_blocked: bool


@dataclass
class ArticlePublishability:
    """Result of publishability check for an article."""
    is_publishable: bool
    can_admin_override: bool
    category_statuses: List[CategoryReviewStatus]
    overall_message: str
    requires_all_categories: bool


def get_category_review_status(article: Article, category: Category) -> CategoryReviewStatus:
    """
    Calculate review status for a specific category on an article.

    Returns CategoryReviewStatus with detailed breakdown.
    """
    # Get reviews for this article-category combination
    reviews = Review.objects.filter(
        article=article,
        category=category
    )

    total_reviews = reviews.count()
    approvals = reviews.filter(decision=Review.Decision.APPROVE).count()
    rejections = reviews.filter(decision=Review.Decision.REJECT).count()
    changes_requested = reviews.filter(decision=Review.Decision.CHANGES).count()

    # Get category policy (or use defaults)
    try:
        policy = category.policy
    except CategoryPolicy.DoesNotExist:
        # Create default policy values
        policy = CategoryPolicy(
            category=category,
            min_approvals_to_publish=2,
            max_rejections_before_block=1,
            min_required_reviews=2,
            allow_admin_override=True
        )

    # Check if category is blocked due to rejections
    is_blocked = rejections > policy.max_rejections_before_block

    # Check if policy requirements are met
    meets_policy = (
        total_reviews >= policy.min_required_reviews and
        approvals >= policy.min_approvals_to_publish and
        not is_blocked and
        changes_requested == 0  # No pending change requests
    )

    # Generate status message
    if is_blocked:
        message = _('Blocked: Too many rejections (%(rejections)d > %(max)d)') % {
            'rejections': rejections,
            'max': policy.max_rejections_before_block
        }
    elif changes_requested > 0:
        message = _('Changes requested by %(count)d reviewer(s)') % {'count': changes_requested}
    elif total_reviews < policy.min_required_reviews:
        message = _('Needs more reviews: %(current)d/%(required)d') % {
            'current': total_reviews,
            'required': policy.min_required_reviews
        }
    elif approvals < policy.min_approvals_to_publish:
        message = _('Needs more approvals: %(current)d/%(required)d') % {
            'current': approvals,
            'required': policy.min_approvals_to_publish
        }
    elif meets_policy:
        message = _('Ready for publishing')
    else:
        message = _('Review in progress')

    return CategoryReviewStatus(
        category=category,
        total_reviews=total_reviews,
        approvals=approvals,
        rejections=rejections,
        changes_requested=changes_requested,
        meets_policy=meets_policy,
        policy_message=str(message),
        is_blocked=is_blocked
    )


def is_article_publishable(article: Article) -> ArticlePublishability:
    """
    Determine if an article is ready to be published based on reviewer assignments.

    Args:
        article: The article to check

    Returns:
        ArticlePublishability with detailed status
    """
    # Check if article has reviewer assignments
    pending_assignments = article.reviewer_assignments.filter(status='PENDING')

    if not pending_assignments.exists():
        return ArticlePublishability(
            is_publishable=True,
            can_admin_override=True,
            category_statuses=[],
            overall_message=str(_('No pending reviewer assignments')),
            requires_all_categories=False
        )

    # Check reviews from assigned reviewers
    assigned_reviewers = pending_assignments.values_list('reviewer_id', flat=True)
    reviews = article.reviews.filter(reviewer_id__in=assigned_reviewers)

    if not reviews.exists():
        return ArticlePublishability(
            is_publishable=False,
            can_admin_override=True,
            category_statuses=[],
            overall_message=str(_('Waiting for reviewer submissions')),
            requires_all_categories=False
        )

    # Check if all required reviews are approvals
    approvals = reviews.filter(decision=Review.Decision.APPROVE).count()
    rejections = reviews.filter(decision=Review.Decision.REJECT).count()
    changes = reviews.filter(decision=Review.Decision.CHANGES).count()

    is_publishable = rejections == 0 and changes == 0

    # Generate message
    if rejections > 0:
        message = str(_('Article has been rejected'))
    elif changes > 0:
        message = str(_('Changes have been requested'))
    elif approvals == reviews.count():
        message = str(_('Article is ready for publishing'))
    else:
        message = str(_('Waiting for reviewer approval'))

    return ArticlePublishability(
        is_publishable=is_publishable,
        can_admin_override=True,
        category_statuses=[],
        overall_message=message,
        requires_all_categories=False
    )


def get_reviewer_queue(user) -> Dict:
    """
    Get the review queue for a reviewer.

    Returns dict with:
        - articles: list of articles assigned to reviewer
        - total_pending: total count of articles needing review
    """
    from .models import Article, ReviewerAssignment

    if not user.is_reviewer and not user.is_superuser:
        return {'articles': [], 'total_pending': 0}

    # Get articles assigned to this reviewer that are in review status
    if user.is_superuser:
        # Superuser can see all articles in review
        reviewable_assignments = ReviewerAssignment.objects.filter(
            status='PENDING'
        ).select_related('article')
    else:
        # Get assignments for this reviewer
        reviewable_assignments = ReviewerAssignment.objects.filter(
            reviewer=user,
            status='PENDING'
        ).select_related('article')

    articles = [assignment.article for assignment in reviewable_assignments]

    return {
        'articles': articles,
        'total_pending': len(articles)
    }


def get_admin_dashboard_stats() -> Dict:
    """
    Get statistics for admin dashboard.
    """
    from .models import Article

    stats = {
        'pending_admin': Article.objects.filter(
            status=Article.ArticleStatus.PENDING_ADMIN
        ).count(),
        'in_review': Article.objects.filter(
            status=Article.ArticleStatus.IN_REVIEW
        ).count(),
        'changes_requested': Article.objects.filter(
            status=Article.ArticleStatus.CHANGES_REQUESTED
        ).count(),
        'published': Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).count(),
        'rejected': Article.objects.filter(
            status=Article.ArticleStatus.REJECTED
        ).count(),
        'total': Article.objects.count(),
    }

    # Get articles ready for publishing
    ready_for_publish = []
    in_review_articles = Article.objects.filter(
        status__in=[Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.CHANGES_REQUESTED]
    )

    for article in in_review_articles:
        publishability = is_article_publishable(article)
        if publishability.is_publishable:
            ready_for_publish.append({
                'article': article,
                'publishability': publishability
            })

    stats['ready_for_publish'] = ready_for_publish
    stats['ready_count'] = len(ready_for_publish)

    return stats


def update_article_status_from_reviews(article: Article) -> Optional[str]:
    """
    Automatically update article status based on current reviews.

    Called after a new review is submitted.

    Returns the new status if changed, None otherwise.
    """
    publishability = is_article_publishable(article)

    # Check if any category has changes requested
    has_changes = any(s.changes_requested > 0 for s in publishability.category_statuses)

    # Check if any category is blocked
    is_blocked = any(s.is_blocked for s in publishability.category_statuses)

    old_status = article.status
    new_status = None

    if has_changes and article.status == Article.ArticleStatus.IN_REVIEW:
        # Move to changes requested
        article.status = Article.ArticleStatus.CHANGES_REQUESTED
        article.save(update_fields=['status'])
        new_status = article.status

    # Note: We don't auto-reject or auto-publish - that's admin's job
    # But we can flag the article appropriately

    return new_status


def search_published_articles(query: str, language: str = 'uz'):
    """
    Search published articles by title, content, keywords, and category names.

    Args:
        query: Search query string
        language: Language code (uz, ru, en)

    Returns:
        QuerySet of matching published articles
    """
    from django.db.models import Q

    if not query:
        return Article.objects.filter(status=Article.ArticleStatus.PUBLISHED)

    query = query.strip()

    # Build Q objects for each field
    title_field = f'title_{language}'
    content_field = f'content_{language}'

    q_objects = Q(**{f'{title_field}__icontains': query})
    q_objects |= Q(**{f'{content_field}__icontains': query})

    # Search in keywords
    q_objects |= Q(keywords__name__icontains=query)

    # Search in category names
    cat_name_field = f'categories__name_{language}'
    q_objects |= Q(**{f'{cat_name_field}__icontains': query})

    return Article.objects.filter(
        status=Article.ArticleStatus.PUBLISHED
    ).filter(q_objects).distinct()
