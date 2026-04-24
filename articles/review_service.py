"""
Service layer for processing review results.
Handles article status updates, notifications, and emails after a review is submitted.
"""
import logging
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Article, Review, ReviewerAssignment

logger = logging.getLogger(__name__)


def process_review_result(review: Review, is_new: bool = True) -> None:
    """
    Central function to process a review after it is saved.

    This function:
    1. Syncs the ReviewerAssignment status with the review decision
    2. Removes other pending reviewer assignments (first reviewer wins)
    3. Updates the article status based on the review decision
    4. Creates in-site notifications for author and admins
    5. Sends email notifications (fail-safe)

    Args:
        review: The Review instance that was just saved
        is_new: Whether this is a newly created review
    """
    article = review.article
    reviewer = review.reviewer
    decision = review.decision
    comment = review.comment or ''

    logger.info(
        f"Processing review: article='{article.title_uz}', "
        f"reviewer={reviewer.username}, decision={decision}, is_new={is_new}"
    )

    with transaction.atomic():
        # 1. Sync ReviewerAssignment status
        _sync_reviewer_assignment(article, reviewer, decision, comment)

        # 2. Remove other pending reviewer assignments (first reviewer wins)
        if is_new:
            _remove_other_pending_assignments(article, reviewer)

        # 3. Update article status
        _update_article_status(article, reviewer, decision, comment)

    # 4-5. Notifications and emails (outside transaction — should not roll back review)
    _notify_author(article, review, reviewer)
    _notify_admins(article, review, reviewer)


def _sync_reviewer_assignment(article, reviewer, decision, comment):
    """Sync the ReviewerAssignment record with the review decision."""
    assignment, created = ReviewerAssignment.objects.get_or_create(
        article=article,
        reviewer=reviewer,
        defaults={
            'status': ReviewerAssignment.AssignmentStatus.PENDING,
        }
    )

    if decision == Review.Decision.APPROVE:
        assignment.mark_approved(comment)
    elif decision == Review.Decision.CHANGES:
        assignment.mark_changes_requested(comment)
    elif decision == Review.Decision.REJECT:
        assignment.mark_rejected(comment)


def _remove_other_pending_assignments(article, first_reviewer):
    """
    Remove all other pending reviewer assignments after first reviewer submits.
    Only the first reviewer's decision counts.
    """
    removed_count = ReviewerAssignment.objects.filter(
        article=article,
        status=ReviewerAssignment.AssignmentStatus.PENDING
    ).exclude(
        reviewer=first_reviewer
    ).delete()[0]

    if removed_count > 0:
        logger.info(
            f"Removed {removed_count} pending reviewer assignment(s) for article "
            f"'{article.title_uz}' after first review by {first_reviewer.username}"
        )


def _update_article_status(article, reviewer, decision, comment):
    """Update article status based on review decision."""
    old_status = article.status

    if decision == Review.Decision.APPROVE:
        # Auto-publish on approval
        if article.status in [
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW,
        ]:
            article.status = Article.ArticleStatus.PUBLISHED
            article.published_at = timezone.now()
            article.admin_decision_at = timezone.now()
            article.save()
            article._log_status_change(
                old_status,
                Article.ArticleStatus.PUBLISHED,
                reviewer,
                f'Auto-published after reviewer approval: {comment or "Approved"}'
            )
            logger.info(f"Article '{article.title_uz}' auto-published after approval")

    elif decision == Review.Decision.CHANGES:
        if article.status in [
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW,
        ]:
            article.status = Article.ArticleStatus.CHANGES_REQUESTED
            article.save(update_fields=['status', 'updated_at'])
            article._log_status_change(
                old_status,
                Article.ArticleStatus.CHANGES_REQUESTED,
                reviewer,
                f'Changes requested: {comment[:100]}'
            )
            logger.info(f"Article '{article.title_uz}' status -> CHANGES_REQUESTED")

    elif decision == Review.Decision.REJECT:
        if article.status in [
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW,
        ]:
            article.status = Article.ArticleStatus.REJECTED
            article.admin_decision_at = timezone.now()
            article.save(update_fields=['status', 'admin_decision_at', 'updated_at'])
            article._log_status_change(
                old_status,
                Article.ArticleStatus.REJECTED,
                reviewer,
                f'Rejected by reviewer: {comment[:100] if comment else "Rejected"}'
            )
            logger.info(f"Article '{article.title_uz}' status -> REJECTED")


def _notify_author(article, review, reviewer):
    """Send in-site notification and email to article author."""
    try:
        from users.services import notify_review_submitted
        notify_review_submitted(article.author, article, review, reviewer)
    except Exception as e:
        logger.error(f"Failed to notify author about review: {e}", exc_info=True)


def _notify_admins(article, review, reviewer):
    """Send in-site notification and email to all admin users."""
    try:
        from users.models import CustomUser, Notification
        from users.services import create_notification, send_email_notification, get_site_url, get_site_name, get_admin_article_link

        decision_labels = {
            Review.Decision.APPROVE: str(_('Approved')),
            Review.Decision.CHANGES: str(_('Changes Requested')),
            Review.Decision.REJECT: str(_('Rejected')),
        }
        decision_text = decision_labels.get(review.decision, review.decision)

        title = str(_("Review submitted for article"))
        message = str(_(
            "Reviewer %(reviewer)s has submitted a review for article '%(title)s'. "
            "Decision: %(decision)s."
        ) % {
            'reviewer': reviewer.get_full_name() or reviewer.username,
            'title': article.title_uz,
            'decision': decision_text,
        })

        admins = CustomUser.objects.filter(
            Q(role=CustomUser.UserRole.ADMIN) | Q(is_superuser=True),
            is_active=True
        ).distinct()

        site_url = get_site_url()
        article_url = f"{site_url}{article.get_absolute_url()}"

        for admin in admins:
            create_notification(
                user=admin,
                notification_type=Notification.NotificationType.REVIEW_SUBMITTED,
                title=title,
                message=message,
                link=get_admin_article_link(article),
            )

            subject = str(_("[%(site_name)s] Review submitted: %(title)s") % {
                'site_name': get_site_name(),
                'title': article.title_uz[:50],
            })

            send_email_notification(
                user=admin,
                subject=subject,
                template_name='review_submitted_admin',
                context={
                    'article': article,
                    'review': review,
                    'reviewer': reviewer,
                    'decision_text': decision_text,
                    'article_url': article_url,
                },
            )

    except Exception as e:
        logger.error(f"Failed to notify admins about review: {e}", exc_info=True)
