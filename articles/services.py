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
    Determine if an article is ready to be published based on all category policies.

    Args:
        article: The article to check

    Returns:
        ArticlePublishability with detailed status for each category
    """
    categories = article.categories.all()

    if not categories.exists():
        return ArticlePublishability(
            is_publishable=False,
            can_admin_override=True,
            category_statuses=[],
            overall_message=str(_('Article has no categories assigned')),
            requires_all_categories=True
        )

    # Check status for each category
    category_statuses = []
    all_meet_policy = True
    any_meets_policy = False
    any_blocked = False
    can_override_all = True
    has_changes_requested = False

    for category in categories:
        status = get_category_review_status(article, category)
        category_statuses.append(status)

        if status.meets_policy:
            any_meets_policy = True
        else:
            all_meet_policy = False

        if status.is_blocked:
            any_blocked = True

        if status.changes_requested > 0:
            has_changes_requested = True

        # Check if admin can override for this category
        try:
            if not category.policy.allow_admin_override:
                can_override_all = False
        except CategoryPolicy.DoesNotExist:
            pass  # Default allows override

    # Determine publishability based on review mode
    requires_all = article.review_mode == Article.ReviewMode.ALL_CATEGORIES

    if requires_all:
        is_publishable = all_meet_policy and not any_blocked and not has_changes_requested
    else:
        is_publishable = any_meets_policy and not any_blocked and not has_changes_requested

    # Generate overall message
    if is_publishable:
        message = _('Article is ready for publishing')
    elif any_blocked:
        message = _('Article is blocked due to rejections in one or more categories')
    elif has_changes_requested:
        message = _('Changes have been requested - waiting for author revision')
    elif requires_all and not all_meet_policy:
        met_count = sum(1 for s in category_statuses if s.meets_policy)
        message = _('%(met)d of %(total)d categories meet policy requirements') % {
            'met': met_count,
            'total': len(category_statuses)
        }
    else:
        message = _('Review in progress')

    return ArticlePublishability(
        is_publishable=is_publishable,
        can_admin_override=can_override_all,
        category_statuses=category_statuses,
        overall_message=str(message),
        requires_all_categories=requires_all
    )


def get_reviewer_queue(user) -> Dict:
    """
    Get the review queue for a reviewer, organized by category.

    Returns dict with:
        - categories: list of assigned categories with pending articles
        - total_pending: total count of articles needing review
    """
    from .models import Article

    if not user.is_reviewer and not user.is_superuser:
        return {'categories': [], 'total_pending': 0}

    # Get assigned categories
    if user.is_superuser:
        categories = Category.objects.filter(is_active=True)
    else:
        categories = user.assigned_categories.filter(is_active=True)

    result = []
    total_pending = 0

    for category in categories:
        # Get articles in this category that can be reviewed
        reviewable_articles = Article.objects.filter(
            categories=category,
            status__in=[Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.CHANGES_REQUESTED]
        ).exclude(
            # Exclude articles already reviewed by this user for this category
            reviews__reviewer=user,
            reviews__category=category
        ).distinct()

        count = reviewable_articles.count()
        if count > 0:
            result.append({
                'category': category,
                'pending_count': count,
                'articles': reviewable_articles[:5]  # Preview first 5
            })
            total_pending += count

    return {
        'categories': result,
        'total_pending': total_pending
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
