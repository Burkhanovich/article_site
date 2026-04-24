"""
Django signals for articles app.
Handles automatic processing when reviews are created or updated.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def review_post_save(sender, instance, created, **kwargs):
    """
    Trigger review processing when a Review is created or updated.
    Delegates all business logic to the service layer.
    """
    from .review_service import process_review_result

    try:
        process_review_result(instance, is_new=created)
    except Exception as e:
        logger.error(
            f"Error processing review result for article "
            f"'{instance.article.title_uz}' by reviewer "
            f"'{instance.reviewer.username}': {e}",
            exc_info=True
        )
