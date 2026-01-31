"""
Centralized workflow service for article publishing platform.
Handles all article status transitions with proper notifications and atomic transactions.
"""
import logging
from typing import Optional, List, Tuple
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Article, ReviewerAssignment

logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    """Exception raised for workflow validation errors."""
    pass


class ArticleWorkflow:
    """
    Centralized workflow handler for article status transitions.
    All status changes should go through this class to ensure consistency.
    """

    # Valid transitions map: from_status -> list of allowed to_statuses
    VALID_TRANSITIONS = {
        Article.ArticleStatus.DRAFT: [
            Article.ArticleStatus.PENDING_ADMIN,
        ],
        Article.ArticleStatus.PENDING_ADMIN: [
            Article.ArticleStatus.IN_REVIEW,
            Article.ArticleStatus.CHANGES_REQUESTED,
            Article.ArticleStatus.PUBLISHED,
            Article.ArticleStatus.REJECTED,
            Article.ArticleStatus.DRAFT,  # Reset to draft
        ],
        Article.ArticleStatus.IN_REVIEW: [
            Article.ArticleStatus.CHANGES_REQUESTED,
            Article.ArticleStatus.PUBLISHED,
            Article.ArticleStatus.REJECTED,
            Article.ArticleStatus.PENDING_ADMIN,  # Send back to admin
        ],
        Article.ArticleStatus.CHANGES_REQUESTED: [
            Article.ArticleStatus.PENDING_ADMIN,  # Author resubmits
            Article.ArticleStatus.PUBLISHED,  # Auto-publish on resubmit
            Article.ArticleStatus.REJECTED,
            Article.ArticleStatus.DRAFT,  # Reset to draft
        ],
        Article.ArticleStatus.REJECTED: [
            Article.ArticleStatus.DRAFT,  # Allow author to start over
        ],
        Article.ArticleStatus.PUBLISHED: [
            Article.ArticleStatus.DRAFT,  # Unpublish (rare)
        ],
    }

    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> bool:
        """Check if a status transition is valid."""
        allowed = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in allowed

    @classmethod
    @transaction.atomic
    def submit_article(cls, article: Article, user) -> Tuple[bool, str]:
        """
        Author submits article for admin review.

        Args:
            article: The Article instance
            user: The user submitting (should be the author)

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_admin_article_submitted

        # Validate user is author
        if user != article.author:
            return False, str(_("Only the author can submit this article."))

        # Validate current status allows submission
        if article.status not in [Article.ArticleStatus.DRAFT, Article.ArticleStatus.CHANGES_REQUESTED]:
            return False, str(_("Article cannot be submitted in its current status."))

        old_status = article.status
        is_resubmission = old_status == Article.ArticleStatus.CHANGES_REQUESTED

        # Update status
        article.status = Article.ArticleStatus.PENDING_ADMIN
        article.submitted_at = timezone.now()
        article.save(update_fields=['status', 'submitted_at', 'updated_at'])

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.PENDING_ADMIN,
            user,
            'Author resubmitted' if is_resubmission else 'Author submitted'
        )

        # Notify admins
        notify_admin_article_submitted(article, user)

        # If this is a resubmission after changes, notify reviewers too
        if is_resubmission:
            cls._notify_resubmission(article)

        logger.info(f"Article '{article.title_uz}' submitted by {user.username}")
        return True, str(_("Article submitted successfully."))

    @classmethod
    @transaction.atomic
    def submit_and_auto_publish(cls, article: Article, user) -> Tuple[bool, str]:
        """
        Author resubmits article and it gets auto-published.
        This is used when author makes changes and resubmits.

        Args:
            article: The Article instance
            user: The user submitting (should be the author)

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_all_parties_published

        # Validate user is author
        if user != article.author:
            return False, str(_("Only the author can submit this article."))

        # Validate current status is CHANGES_REQUESTED
        if article.status != Article.ArticleStatus.CHANGES_REQUESTED:
            return False, str(_("Auto-publish only works when resubmitting after changes requested."))

        old_status = article.status

        # Update status directly to PUBLISHED
        article.status = Article.ArticleStatus.PUBLISHED
        article.published_at = timezone.now()
        article.admin_decision_at = timezone.now()
        article.save(update_fields=['status', 'published_at', 'admin_decision_at', 'updated_at'])

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.PUBLISHED,
            user,
            'Auto-published after author resubmission'
        )

        # Notify all parties
        notify_all_parties_published(article)

        logger.info(f"Article '{article.title_uz}' auto-published after resubmission by {user.username}")
        return True, str(_("Article has been published successfully."))

    @classmethod
    @transaction.atomic
    def send_to_review(cls, article: Article, admin_user, reviewers: List = None, note: str = None) -> Tuple[bool, str]:
        """
        Admin sends article to reviewers.

        Args:
            article: The Article instance
            admin_user: The admin user
            reviewers: Optional list of specific reviewers to assign
            note: Optional admin note

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_reviewer_article_assigned, notify_reviewers_for_article

        # Validate status
        if article.status != Article.ArticleStatus.PENDING_ADMIN:
            return False, str(_("Only pending articles can be sent to review."))

        old_status = article.status

        # Update status
        article.status = Article.ArticleStatus.IN_REVIEW
        if note:
            article.admin_note = note
        article.save(update_fields=['status', 'admin_note', 'updated_at'])

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.IN_REVIEW,
            admin_user,
            note or 'Sent to review'
        )

        # Assign specific reviewers if provided
        if reviewers:
            for reviewer in reviewers:
                assignment, created = ReviewerAssignment.objects.get_or_create(
                    article=article,
                    reviewer=reviewer,
                    defaults={
                        'assigned_by': admin_user,
                        'status': ReviewerAssignment.AssignmentStatus.PENDING,
                    }
                )
                if created:
                    notify_reviewer_article_assigned(reviewer, article, admin_user)
        else:
            # Notify category-based reviewers
            notify_reviewers_for_article(article, admin_user)

        logger.info(f"Article '{article.title_uz}' sent to review by {admin_user.username}")
        return True, str(_("Article sent to review successfully."))

    @classmethod
    @transaction.atomic
    def assign_reviewers(cls, article: Article, reviewers: List, admin_user) -> Tuple[bool, str, int]:
        """
        Admin assigns specific reviewers to an article.

        Args:
            article: The Article instance
            reviewers: List of reviewer users
            admin_user: The admin making the assignment

        Returns:
            Tuple of (success, message, count_assigned)
        """
        from users.services import notify_reviewer_article_assigned

        if article.status not in [Article.ArticleStatus.PENDING_ADMIN, Article.ArticleStatus.IN_REVIEW]:
            return False, str(_("Reviewers can only be assigned to pending or in-review articles.")), 0

        count_assigned = 0
        for reviewer in reviewers:
            assignment, created = ReviewerAssignment.objects.get_or_create(
                article=article,
                reviewer=reviewer,
                defaults={
                    'assigned_by': admin_user,
                    'status': ReviewerAssignment.AssignmentStatus.PENDING,
                }
            )
            if created:
                notify_reviewer_article_assigned(reviewer, article, admin_user)
                count_assigned += 1

        logger.info(f"Assigned {count_assigned} reviewer(s) to article '{article.title_uz}'")
        return True, str(_("%(count)d reviewer(s) assigned.") % {'count': count_assigned}), count_assigned

    @classmethod
    @transaction.atomic
    def reviewer_approve(cls, article: Article, reviewer, comment: str = None) -> Tuple[bool, str]:
        """
        Reviewer approves the article.
        When approved, the article is automatically published.

        Args:
            article: The Article instance
            reviewer: The reviewer user
            comment: Optional comment

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_review_submitted, notify_all_parties_published

        # Get or create assignment
        assignment, created = ReviewerAssignment.objects.get_or_create(
            article=article,
            reviewer=reviewer,
            defaults={
                'status': ReviewerAssignment.AssignmentStatus.PENDING,
            }
        )

        assignment.mark_approved(comment)

        # Create a Review record for legacy compatibility
        from .models import Review, Category
        # Use the first category from the article for the review
        category = article.categories.first()
        if category:
            Review.objects.update_or_create(
                article=article,
                reviewer=reviewer,
                category=category,
                defaults={
                    'decision': Review.Decision.APPROVE,
                    'comment': comment,
                }
            )

            # Notify author about review
            review = Review.objects.get(article=article, reviewer=reviewer, category=category)
            notify_review_submitted(article.author, article, review, reviewer)

        # AUTO-PUBLISH: When reviewer approves, article is automatically published
        if article.status in [Article.ArticleStatus.IN_REVIEW, Article.ArticleStatus.PENDING_ADMIN]:
            old_status = article.status
            article.status = Article.ArticleStatus.PUBLISHED
            article.published_at = timezone.now()
            article.admin_decision_at = timezone.now()
            article.save()

            # Log the status change
            article._log_status_change(
                old_status,
                Article.ArticleStatus.PUBLISHED,
                reviewer,
                f'Auto-published after reviewer approval: {comment or "Approved"}'
            )

            # Notify all parties about publication
            notify_all_parties_published(article)

            logger.info(f"Article '{article.title_uz}' auto-published after approval by {reviewer.username}")
            return True, str(_("Maqola tasdiqlandi va nashr qilindi."))

        logger.info(f"Reviewer {reviewer.username} approved article '{article.title_uz}'")
        return True, str(_("Maqola tasdiqlandi."))

    @classmethod
    @transaction.atomic
    def reviewer_request_changes(cls, article: Article, reviewer, comment: str) -> Tuple[bool, str]:
        """
        Reviewer requests changes to the article.

        Args:
            article: The Article instance
            reviewer: The reviewer user
            comment: Required comment explaining needed changes

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_review_submitted, notify_changes_requested

        if not comment:
            return False, str(_("Comment is required when requesting changes."))

        # Get or create assignment
        assignment, created = ReviewerAssignment.objects.get_or_create(
            article=article,
            reviewer=reviewer,
            defaults={
                'status': ReviewerAssignment.AssignmentStatus.PENDING,
            }
        )

        assignment.mark_changes_requested(comment)

        # Update article status if it's in review
        if article.status == Article.ArticleStatus.IN_REVIEW:
            old_status = article.status
            article.status = Article.ArticleStatus.CHANGES_REQUESTED
            article.save(update_fields=['status', 'updated_at'])
            article._log_status_change(
                old_status,
                Article.ArticleStatus.CHANGES_REQUESTED,
                reviewer,
                f'Changes requested: {comment[:100]}'
            )

        # Create a Review record for legacy compatibility
        from .models import Review
        category = article.categories.first()
        if category:
            Review.objects.update_or_create(
                article=article,
                reviewer=reviewer,
                category=category,
                defaults={
                    'decision': Review.Decision.CHANGES,
                    'comment': comment,
                }
            )

            review = Review.objects.get(article=article, reviewer=reviewer, category=category)
            notify_review_submitted(article.author, article, review, reviewer)

        # Notify author about changes requested
        notify_changes_requested(article.author, article, comment)

        logger.info(f"Reviewer {reviewer.username} requested changes for article '{article.title_uz}'")
        return True, str(_("Changes requested from author."))

    @classmethod
    @transaction.atomic
    def publish_article(cls, article: Article, admin_user, note: str = None) -> Tuple[bool, str]:
        """
        Admin publishes the article.

        Args:
            article: The Article instance
            admin_user: The admin user
            note: Optional admin note

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_all_parties_published

        # Validate status
        if article.status not in [
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW,
            Article.ArticleStatus.CHANGES_REQUESTED
        ]:
            return False, str(_("Article cannot be published in its current status."))

        old_status = article.status

        # Update status
        article.status = Article.ArticleStatus.PUBLISHED
        article.admin_decision_by = admin_user
        article.admin_decision_at = timezone.now()
        article.published_at = timezone.now()
        if note:
            article.admin_note = note
        article.save()

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.PUBLISHED,
            admin_user,
            note or 'Published'
        )

        # Notify all parties
        notify_all_parties_published(article)

        logger.info(f"Article '{article.title_uz}' published by {admin_user.username}")
        return True, str(_("Article published successfully."))

    @classmethod
    @transaction.atomic
    def reject_article(cls, article: Article, admin_user, reason: str = None) -> Tuple[bool, str]:
        """
        Admin rejects the article.

        Args:
            article: The Article instance
            admin_user: The admin user
            reason: Optional rejection reason

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_article_rejected

        # Validate status
        if article.status not in [
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW,
            Article.ArticleStatus.CHANGES_REQUESTED
        ]:
            return False, str(_("Article cannot be rejected in its current status."))

        old_status = article.status

        # Update status
        article.status = Article.ArticleStatus.REJECTED
        article.admin_decision_by = admin_user
        article.admin_decision_at = timezone.now()
        if reason:
            article.admin_note = reason
        article.save()

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.REJECTED,
            admin_user,
            reason or 'Rejected'
        )

        # Notify author
        notify_article_rejected(article.author, article, reason, admin_user)

        logger.info(f"Article '{article.title_uz}' rejected by {admin_user.username}")
        return True, str(_("Article rejected."))

    @classmethod
    @transaction.atomic
    def request_changes_from_author(cls, article: Article, admin_user, note: str = None) -> Tuple[bool, str]:
        """
        Admin requests changes from author.

        Args:
            article: The Article instance
            admin_user: The admin user
            note: Optional note explaining needed changes

        Returns:
            Tuple of (success, message)
        """
        from users.services import notify_changes_requested

        # Validate status
        if article.status not in [Article.ArticleStatus.PENDING_ADMIN, Article.ArticleStatus.IN_REVIEW]:
            return False, str(_("Cannot request changes for article in its current status."))

        old_status = article.status

        # Update status
        article.status = Article.ArticleStatus.CHANGES_REQUESTED
        if note:
            article.admin_note = note
        article.save(update_fields=['status', 'admin_note', 'updated_at'])

        # Log the change
        article._log_status_change(
            old_status,
            Article.ArticleStatus.CHANGES_REQUESTED,
            admin_user,
            note or 'Changes requested'
        )

        # Notify author
        notify_changes_requested(article.author, article, note)

        logger.info(f"Changes requested for article '{article.title_uz}' by {admin_user.username}")
        return True, str(_("Changes requested from author."))

    @classmethod
    def _notify_resubmission(cls, article: Article):
        """Notify relevant parties about article resubmission."""
        from users.services import notify_article_resubmitted
        from users.models import CustomUser
        from django.db.models import Q

        # Get assigned reviewers
        reviewer_ids = article.reviewer_assignments.values_list('reviewer_id', flat=True)
        reviewers = list(CustomUser.objects.filter(id__in=reviewer_ids))

        # Get admins
        admins = list(CustomUser.objects.filter(
            Q(role=CustomUser.UserRole.ADMIN) | Q(is_superuser=True),
            is_active=True
        ).distinct())

        # Combine and deduplicate
        recipients = {u.id: u for u in reviewers + admins}.values()

        notify_article_resubmitted(article, list(recipients))

        # Reset reviewer assignments to pending
        article.reviewer_assignments.update(
            status=ReviewerAssignment.AssignmentStatus.PENDING,
            reviewed_at=None
        )
