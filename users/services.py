"""
Email and notification services for the article publishing platform.
Handles sending emails and creating in-site notifications.
"""
import logging
from typing import List, Optional, Dict, Any
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _, get_language, activate
from django.urls import reverse

from .models import CustomUser, Notification

logger = logging.getLogger(__name__)


def get_site_url() -> str:
    """Get the site URL from settings."""
    return getattr(settings, 'SITE_URL', 'http://localhost:8000')


def get_site_name() -> str:
    """Get the site name from settings."""
    return getattr(settings, 'SITE_NAME', 'Article Publishing Platform')


def send_email_notification(
    user: CustomUser,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    language: str = None
) -> bool:
    """
    Send an email notification to a user.

    Args:
        user: The recipient user
        subject: Email subject
        template_name: Name of the email template (without extension)
        context: Context data for the template
        language: Language code (uz, ru, en). If None, uses user's preferred language

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not user.email:
        logger.warning(f"Cannot send email to user {user.username}: no email address")
        return False

    # Determine language
    lang = language or getattr(user, 'preferred_language', None) or get_language() or 'uz'

    # Temporarily activate the user's language
    current_lang = get_language()
    activate(lang)

    try:
        # Add common context
        context.update({
            'user': user,
            'site_url': get_site_url(),
            'site_name': get_site_name(),
            'language': lang,
        })

        # Render templates
        html_template = f'emails/{template_name}.html'
        txt_template = f'emails/{template_name}.txt'

        try:
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(txt_template, context)
        except Exception as e:
            # Fallback to plain text if templates don't exist
            logger.warning(f"Email template {template_name} not found, using fallback: {e}")
            text_content = context.get('message', str(subject))
            html_content = f"<html><body><p>{text_content}</p></body></html>"

        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Email sent to {user.email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {e}")
        return False
    finally:
        # Restore original language
        activate(current_lang)


def create_notification(
    user: CustomUser,
    notification_type: str,
    title: str,
    message: str,
    link: str = None
) -> Notification:
    """
    Create an in-site notification for a user.

    Args:
        user: The recipient user
        notification_type: Type of notification (from Notification.NotificationType)
        title: Notification title
        message: Notification message
        link: Optional URL to link to

    Returns:
        The created Notification object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )
    logger.info(f"Notification created for {user.username}: {title}")
    return notification


def notify_reviewer_assigned(
    user: CustomUser,
    categories: List,
    assigned_by: CustomUser = None
) -> bool:
    """
    Notify a user that they have been assigned as a reviewer.

    Args:
        user: The user who was assigned as reviewer
        categories: List of Category objects they are assigned to
        assigned_by: The admin who made the assignment (optional)

    Returns:
        True if notifications were sent successfully
    """
    category_names = ', '.join([cat.name_uz for cat in categories]) if categories else 'N/A'
    site_url = get_site_url()
    dashboard_url = f"{site_url}{reverse('articles:reviewer_dashboard')}"

    # Create in-site notification
    title = str(_("You have been assigned as a Reviewer"))
    message = str(_(
        "You have been assigned as a reviewer (Red Collegiya member). "
        "Your assigned categories: %(categories)s. "
        "Please visit the Reviewer Dashboard to see articles waiting for your review."
    ) % {'categories': category_names})

    create_notification(
        user=user,
        notification_type=Notification.NotificationType.REVIEWER_ASSIGNED,
        title=title,
        message=message,
        link=reverse('articles:reviewer_dashboard'),
    )

    # Send email
    context = {
        'categories': categories,
        'category_names': category_names,
        'assigned_by': assigned_by,
        'dashboard_url': dashboard_url,
    }

    subject = str(_("[%(site_name)s] You have been assigned as a Reviewer") % {
        'site_name': get_site_name()
    })

    return send_email_notification(
        user=user,
        subject=subject,
        template_name='reviewer_assigned',
        context=context,
    )


def notify_article_for_review(
    reviewer: CustomUser,
    article,
    categories: List
) -> bool:
    """
    Notify a reviewer that an article is ready for their review.

    Args:
        reviewer: The reviewer to notify
        article: The Article object to be reviewed
        categories: Categories this reviewer should review for

    Returns:
        True if notifications were sent successfully
    """
    site_url = get_site_url()
    article_url = f"{site_url}{article.get_absolute_url()}"
    category_names = ', '.join([cat.name_uz for cat in categories])

    # Create in-site notification
    title = str(_("New article assigned for review"))
    message = str(_(
        "Article '%(title)s' by %(author)s has been assigned for your review. "
        "Categories: %(categories)s."
    ) % {
        'title': article.title_uz,
        'author': article.author.username,
        'categories': category_names,
    })

    create_notification(
        user=reviewer,
        notification_type=Notification.NotificationType.ARTICLE_FOR_REVIEW,
        title=title,
        message=message,
        link=article.get_absolute_url(),
    )

    # Send email
    context = {
        'article': article,
        'categories': categories,
        'category_names': category_names,
        'article_url': article_url,
    }

    subject = str(_("[%(site_name)s] New article assigned for review: %(title)s") % {
        'site_name': get_site_name(),
        'title': article.title_uz[:50],
    })

    return send_email_notification(
        user=reviewer,
        subject=subject,
        template_name='article_for_review',
        context=context,
    )


def notify_review_submitted(
    author: CustomUser,
    article,
    review,
    reviewer: CustomUser
) -> bool:
    """
    Notify an author that a review has been submitted for their article.

    Args:
        author: The article author to notify
        article: The Article object
        review: The Review object
        reviewer: The reviewer who submitted the review

    Returns:
        True if notifications were sent successfully
    """
    site_url = get_site_url()
    article_url = f"{site_url}{article.get_absolute_url()}"

    # Determine decision text
    decision_texts = {
        'APPROVE': _('Approved'),
        'CHANGES': _('Changes Requested'),
        'REJECT': _('Rejected'),
    }
    decision_text = decision_texts.get(review.decision, review.decision)

    # Create in-site notification
    title = str(_("Review received for your article"))
    message = str(_(
        "Your article '%(title)s' has received a review. "
        "Decision: %(decision)s. Category: %(category)s."
    ) % {
        'title': article.title_uz,
        'decision': decision_text,
        'category': review.category.name_uz,
    })

    if review.comment:
        message += str(_(" Comment: %(comment)s") % {'comment': review.comment[:200]})

    create_notification(
        user=author,
        notification_type=Notification.NotificationType.REVIEW_SUBMITTED,
        title=title,
        message=message,
        link=article.get_absolute_url(),
    )

    # Send email
    context = {
        'article': article,
        'review': review,
        'reviewer': reviewer,
        'decision_text': decision_text,
        'article_url': article_url,
    }

    subject = str(_("[%(site_name)s] Review update for your article: %(title)s") % {
        'site_name': get_site_name(),
        'title': article.title_uz[:50],
    })

    return send_email_notification(
        user=author,
        subject=subject,
        template_name='review_submitted',
        context=context,
    )


def notify_article_published(author: CustomUser, article) -> bool:
    """
    Notify an author that their article has been published.

    Args:
        author: The article author to notify
        article: The Article object

    Returns:
        True if notifications were sent successfully
    """
    site_url = get_site_url()
    article_url = f"{site_url}{article.get_absolute_url()}"

    # Create in-site notification
    title = str(_("Your article has been published!"))
    message = str(_(
        "Congratulations! Your article '%(title)s' has been published and is now visible to readers."
    ) % {'title': article.title_uz})

    create_notification(
        user=author,
        notification_type=Notification.NotificationType.ARTICLE_PUBLISHED,
        title=title,
        message=message,
        link=article.get_absolute_url(),
    )

    # Send email
    context = {
        'article': article,
        'article_url': article_url,
    }

    subject = str(_("[%(site_name)s] Your article has been published: %(title)s") % {
        'site_name': get_site_name(),
        'title': article.title_uz[:50],
    })

    return send_email_notification(
        user=author,
        subject=subject,
        template_name='article_published',
        context=context,
    )


def notify_article_rejected(
    author: CustomUser,
    article,
    reason: str = None,
    rejected_by: CustomUser = None
) -> bool:
    """
    Notify an author that their article has been rejected.

    Args:
        author: The article author to notify
        article: The Article object
        reason: Rejection reason
        rejected_by: Admin who rejected the article

    Returns:
        True if notifications were sent successfully
    """
    site_url = get_site_url()
    article_url = f"{site_url}{article.get_absolute_url()}"

    # Create in-site notification
    title = str(_("Your article has been rejected"))
    message = str(_(
        "Your article '%(title)s' has been rejected."
    ) % {'title': article.title_uz})

    if reason:
        message += str(_(" Reason: %(reason)s") % {'reason': reason})

    create_notification(
        user=author,
        notification_type=Notification.NotificationType.ARTICLE_REJECTED,
        title=title,
        message=message,
        link=article.get_absolute_url(),
    )

    # Send email
    context = {
        'article': article,
        'article_url': article_url,
        'reason': reason,
        'rejected_by': rejected_by,
    }

    subject = str(_("[%(site_name)s] Your article has been rejected: %(title)s") % {
        'site_name': get_site_name(),
        'title': article.title_uz[:50],
    })

    return send_email_notification(
        user=author,
        subject=subject,
        template_name='article_rejected',
        context=context,
    )


def notify_changes_requested(
    author: CustomUser,
    article,
    reason: str = None
) -> bool:
    """
    Notify an author that changes have been requested for their article.

    Args:
        author: The article author to notify
        article: The Article object
        reason: Reason for requesting changes

    Returns:
        True if notifications were sent successfully
    """
    site_url = get_site_url()
    edit_url = f"{site_url}{reverse('articles:edit', kwargs={'slug': article.slug})}"

    # Create in-site notification
    title = str(_("Changes requested for your article"))
    message = str(_(
        "Changes have been requested for your article '%(title)s'. "
        "Please review the feedback and make necessary updates."
    ) % {'title': article.title_uz})

    if reason:
        message += str(_(" Feedback: %(reason)s") % {'reason': reason})

    create_notification(
        user=author,
        notification_type=Notification.NotificationType.CHANGES_REQUESTED,
        title=title,
        message=message,
        link=reverse('articles:edit', kwargs={'slug': article.slug}),
    )

    # Send email
    context = {
        'article': article,
        'edit_url': edit_url,
        'reason': reason,
    }

    subject = str(_("[%(site_name)s] Changes requested for your article: %(title)s") % {
        'site_name': get_site_name(),
        'title': article.title_uz[:50],
    })

    return send_email_notification(
        user=author,
        subject=subject,
        template_name='changes_requested',
        context=context,
    )


def notify_reviewers_for_article(article, admin_user: CustomUser = None) -> int:
    """
    Notify all eligible reviewers when an article is sent to review.

    Args:
        article: The Article object sent to review
        admin_user: The admin who sent the article to review

    Returns:
        Number of reviewers notified
    """
    notified_count = 0

    # Get all categories of the article
    categories = article.categories.all()

    # Track which reviewers have been notified
    notified_reviewers = set()

    for category in categories:
        # Get reviewers assigned to this category
        reviewers = category.reviewers.filter(role=CustomUser.UserRole.REVIEWER)

        for reviewer in reviewers:
            if reviewer.id not in notified_reviewers:
                # Get all categories this reviewer can review for this article
                reviewer_categories = [
                    cat for cat in categories
                    if reviewer.can_review_category(cat)
                ]

                if reviewer_categories:
                    notify_article_for_review(reviewer, article, reviewer_categories)
                    notified_reviewers.add(reviewer.id)
                    notified_count += 1

    logger.info(f"Notified {notified_count} reviewers for article: {article.title_uz}")
    return notified_count
