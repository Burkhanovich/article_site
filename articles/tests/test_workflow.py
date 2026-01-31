"""
Tests for article workflow service.
Tests cover the complete editorial workflow including:
- Author submission triggers admin notification
- Admin assigns reviewers triggers reviewer notifications
- Reviewer actions (approve, request changes)
- Author resubmit auto-publishes article
- Status transitions work correctly
"""
import pytest
from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import patch, MagicMock

from articles.models import Article, Category, CategoryPolicy, Review, ReviewerAssignment
from articles.workflow import ArticleWorkflow, WorkflowError
from users.models import CustomUser, Notification


class WorkflowTestBase(TestCase):
    """Base test class with common setup."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data that doesn't change between tests."""
        # Create admin user
        cls.admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            role=CustomUser.UserRole.ADMIN,
            is_staff=True,
        )

        # Create superuser
        cls.superuser = CustomUser.objects.create_superuser(
            username='superadmin',
            email='superadmin@test.com',
            password='superpass123',
        )

        # Create author user
        cls.author = CustomUser.objects.create_user(
            username='author',
            email='author@test.com',
            password='authorpass123',
            role=CustomUser.UserRole.AUTHOR,
        )

        # Create reviewer users
        cls.reviewer1 = CustomUser.objects.create_user(
            username='reviewer1',
            email='reviewer1@test.com',
            password='reviewer1pass123',
            role=CustomUser.UserRole.REVIEWER,
        )
        cls.reviewer2 = CustomUser.objects.create_user(
            username='reviewer2',
            email='reviewer2@test.com',
            password='reviewer2pass123',
            role=CustomUser.UserRole.REVIEWER,
        )

        # Create category
        cls.category = Category.objects.create(
            name_uz='Test Category',
            name_ru='Test Category RU',
            name_en='Test Category EN',
            slug='test-category',
        )
        cls.category.reviewers.add(cls.reviewer1, cls.reviewer2)

        # Create category policy
        cls.policy = CategoryPolicy.objects.create(
            category=cls.category,
            min_approvals_to_publish=1,
            max_rejections_before_block=1,
            min_required_reviews=1,
        )

    def create_article(self, status=Article.ArticleStatus.DRAFT, author=None):
        """Helper method to create a test article."""
        if author is None:
            author = self.author

        article = Article.objects.create(
            title_uz='Test Article',
            title_ru='Test Article RU',
            title_en='Test Article EN',
            content_uz='Test content',
            content_ru='Test content RU',
            content_en='Test content EN',
            author=author,
            status=status,
        )
        article.categories.add(self.category)
        return article


class TestAuthorSubmitArticle(WorkflowTestBase):
    """Test author submission flow."""

    def test_author_submit_from_draft_success(self):
        """Test that author can submit a draft article."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        success, message = ArticleWorkflow.submit_article(article, self.author)

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.PENDING_ADMIN)
        self.assertIsNotNone(article.submitted_at)

    def test_author_submit_triggers_admin_notification(self):
        """Test that submitting article creates notification for admin."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        # Clear any existing notifications
        Notification.objects.all().delete()

        success, message = ArticleWorkflow.submit_article(article, self.author)

        self.assertTrue(success)

        # Check admin received notification
        admin_notifications = Notification.objects.filter(
            user=self.admin,
            notification_type=Notification.NotificationType.ARTICLE_SUBMITTED
        )
        self.assertTrue(admin_notifications.exists())

        # Check superuser also received notification
        superuser_notifications = Notification.objects.filter(
            user=self.superuser,
            notification_type=Notification.NotificationType.ARTICLE_SUBMITTED
        )
        self.assertTrue(superuser_notifications.exists())

    def test_non_author_cannot_submit(self):
        """Test that only the author can submit their article."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        success, message = ArticleWorkflow.submit_article(article, self.reviewer1)

        self.assertFalse(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.DRAFT)

    def test_cannot_submit_published_article(self):
        """Test that published articles cannot be submitted."""
        article = self.create_article(status=Article.ArticleStatus.PUBLISHED)

        success, message = ArticleWorkflow.submit_article(article, self.author)

        self.assertFalse(success)


class TestAdminAssignReviewers(WorkflowTestBase):
    """Test admin reviewer assignment flow."""

    def test_admin_assign_reviewers_success(self):
        """Test that admin can assign reviewers to an article."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)

        success, message, count = ArticleWorkflow.assign_reviewers(
            article,
            [self.reviewer1, self.reviewer2],
            self.admin
        )

        self.assertTrue(success)
        self.assertEqual(count, 2)

        # Check assignments were created
        assignments = ReviewerAssignment.objects.filter(article=article)
        self.assertEqual(assignments.count(), 2)

    def test_assign_reviewers_triggers_notifications(self):
        """Test that assigning reviewers creates notifications for them."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)

        # Clear existing notifications
        Notification.objects.all().delete()

        success, message, count = ArticleWorkflow.assign_reviewers(
            article,
            [self.reviewer1],
            self.admin
        )

        self.assertTrue(success)

        # Check reviewer received notification
        reviewer_notifications = Notification.objects.filter(
            user=self.reviewer1,
            notification_type=Notification.NotificationType.REVIEWER_ASSIGNMENT
        )
        self.assertTrue(reviewer_notifications.exists())

    def test_send_to_review_with_reviewers(self):
        """Test sending article to review with specific reviewers."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)

        success, message = ArticleWorkflow.send_to_review(
            article,
            self.admin,
            reviewers=[self.reviewer1]
        )

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.IN_REVIEW)

        # Check assignment was created
        self.assertTrue(
            ReviewerAssignment.objects.filter(
                article=article,
                reviewer=self.reviewer1
            ).exists()
        )


class TestReviewerActions(WorkflowTestBase):
    """Test reviewer actions flow."""

    def test_reviewer_approve_success(self):
        """Test that reviewer can approve an article and it gets auto-published."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)

        success, message = ArticleWorkflow.reviewer_approve(
            article,
            self.reviewer1,
            comment='Looks good!'
        )

        self.assertTrue(success)

        # Check assignment status updated
        assignment = ReviewerAssignment.objects.get(
            article=article,
            reviewer=self.reviewer1
        )
        self.assertEqual(
            assignment.status,
            ReviewerAssignment.AssignmentStatus.APPROVED
        )

        # Check article is auto-published
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.PUBLISHED)
        self.assertIsNotNone(article.published_at)

    def test_reviewer_request_changes_success(self):
        """Test that reviewer can request changes."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)

        success, message = ArticleWorkflow.reviewer_request_changes(
            article,
            self.reviewer1,
            comment='Please fix the introduction.'
        )

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.CHANGES_REQUESTED)

    def test_reviewer_request_changes_triggers_author_notification(self):
        """Test that requesting changes notifies the author."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)

        # Clear notifications
        Notification.objects.all().delete()

        success, message = ArticleWorkflow.reviewer_request_changes(
            article,
            self.reviewer1,
            comment='Please revise.'
        )

        self.assertTrue(success)

        # Check author received notification
        author_notifications = Notification.objects.filter(
            user=self.author,
            notification_type=Notification.NotificationType.CHANGES_REQUESTED
        )
        self.assertTrue(author_notifications.exists())

    def test_reviewer_request_changes_requires_comment(self):
        """Test that requesting changes requires a comment."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)

        success, message = ArticleWorkflow.reviewer_request_changes(
            article,
            self.reviewer1,
            comment=''
        )

        self.assertFalse(success)


class TestAuthorResubmitAutoPublish(WorkflowTestBase):
    """Test author resubmission auto-publish flow."""

    def test_resubmit_auto_publish_success(self):
        """Test that resubmitting after changes requested auto-publishes."""
        article = self.create_article(status=Article.ArticleStatus.CHANGES_REQUESTED)

        success, message = ArticleWorkflow.submit_and_auto_publish(article, self.author)

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.PUBLISHED)
        self.assertIsNotNone(article.published_at)

    def test_resubmit_auto_publish_notifies_all_parties(self):
        """Test that auto-publish notifies author, reviewers, and admins."""
        article = self.create_article(status=Article.ArticleStatus.CHANGES_REQUESTED)

        # Create a reviewer assignment
        ReviewerAssignment.objects.create(
            article=article,
            reviewer=self.reviewer1,
            assigned_by=self.admin,
            status=ReviewerAssignment.AssignmentStatus.CHANGES_REQUESTED,
        )

        # Clear notifications
        Notification.objects.all().delete()

        success, message = ArticleWorkflow.submit_and_auto_publish(article, self.author)

        self.assertTrue(success)

        # Check author received notification
        author_notifications = Notification.objects.filter(
            user=self.author,
            notification_type=Notification.NotificationType.ARTICLE_PUBLISHED
        )
        self.assertTrue(author_notifications.exists())

    def test_resubmit_auto_publish_only_from_changes_requested(self):
        """Test that auto-publish only works from CHANGES_REQUESTED status."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        success, message = ArticleWorkflow.submit_and_auto_publish(article, self.author)

        self.assertFalse(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.DRAFT)


class TestStatusTransitions(WorkflowTestBase):
    """Test status transition validation and publish bug fix."""

    def test_valid_transition_draft_to_pending(self):
        """Test valid transition from DRAFT to PENDING_ADMIN."""
        valid = ArticleWorkflow.validate_transition(
            Article.ArticleStatus.DRAFT,
            Article.ArticleStatus.PENDING_ADMIN
        )
        self.assertTrue(valid)

    def test_valid_transition_pending_to_in_review(self):
        """Test valid transition from PENDING_ADMIN to IN_REVIEW."""
        valid = ArticleWorkflow.validate_transition(
            Article.ArticleStatus.PENDING_ADMIN,
            Article.ArticleStatus.IN_REVIEW
        )
        self.assertTrue(valid)

    def test_valid_transition_changes_requested_to_published(self):
        """Test valid transition from CHANGES_REQUESTED to PUBLISHED."""
        valid = ArticleWorkflow.validate_transition(
            Article.ArticleStatus.CHANGES_REQUESTED,
            Article.ArticleStatus.PUBLISHED
        )
        self.assertTrue(valid)

    def test_invalid_transition_draft_to_published(self):
        """Test invalid direct transition from DRAFT to PUBLISHED."""
        valid = ArticleWorkflow.validate_transition(
            Article.ArticleStatus.DRAFT,
            Article.ArticleStatus.PUBLISHED
        )
        self.assertFalse(valid)

    def test_publish_sets_published_at(self):
        """Test that publishing an article sets published_at timestamp."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)
        self.assertIsNone(article.published_at)

        success, message = ArticleWorkflow.publish_article(article, self.admin)

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertIsNotNone(article.published_at)
        self.assertEqual(article.status, Article.ArticleStatus.PUBLISHED)

    def test_publish_article_from_in_review(self):
        """Test publishing an article from IN_REVIEW status."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)

        success, message = ArticleWorkflow.publish_article(article, self.admin)

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.PUBLISHED)

    def test_publish_article_from_changes_requested(self):
        """Test publishing an article from CHANGES_REQUESTED status."""
        article = self.create_article(status=Article.ArticleStatus.CHANGES_REQUESTED)

        success, message = ArticleWorkflow.publish_article(article, self.admin)

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.PUBLISHED)

    def test_cannot_publish_draft_directly(self):
        """Test that DRAFT articles cannot be published directly."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        success, message = ArticleWorkflow.publish_article(article, self.admin)

        self.assertFalse(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.DRAFT)

    def test_reject_article_success(self):
        """Test rejecting an article."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)

        success, message = ArticleWorkflow.reject_article(
            article,
            self.admin,
            reason='Does not meet quality standards.'
        )

        self.assertTrue(success)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.ArticleStatus.REJECTED)
        self.assertEqual(article.admin_note, 'Does not meet quality standards.')


class TestStatusHistory(WorkflowTestBase):
    """Test that status changes are logged correctly."""

    def test_submit_logs_status_change(self):
        """Test that submitting an article logs the status change."""
        article = self.create_article(status=Article.ArticleStatus.DRAFT)

        success, message = ArticleWorkflow.submit_article(article, self.author)

        self.assertTrue(success)

        # Check status history
        history = article.status_history.first()
        self.assertIsNotNone(history)
        self.assertEqual(history.from_status, Article.ArticleStatus.DRAFT)
        self.assertEqual(history.to_status, Article.ArticleStatus.PENDING_ADMIN)
        self.assertEqual(history.changed_by, self.author)

    def test_publish_logs_status_change(self):
        """Test that publishing an article logs the status change."""
        article = self.create_article(status=Article.ArticleStatus.PENDING_ADMIN)

        success, message = ArticleWorkflow.publish_article(article, self.admin)

        self.assertTrue(success)

        # Check status history
        history = article.status_history.first()
        self.assertIsNotNone(history)
        self.assertEqual(history.from_status, Article.ArticleStatus.PENDING_ADMIN)
        self.assertEqual(history.to_status, Article.ArticleStatus.PUBLISHED)
        self.assertEqual(history.changed_by, self.admin)


class TestReviewerAssignmentModel(WorkflowTestBase):
    """Test ReviewerAssignment model methods."""

    def test_mark_approved(self):
        """Test marking assignment as approved."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)
        assignment = ReviewerAssignment.objects.create(
            article=article,
            reviewer=self.reviewer1,
            assigned_by=self.admin,
        )

        assignment.mark_approved(comment='Great article!')

        assignment.refresh_from_db()
        self.assertEqual(
            assignment.status,
            ReviewerAssignment.AssignmentStatus.APPROVED
        )
        self.assertEqual(assignment.review_comment, 'Great article!')
        self.assertIsNotNone(assignment.reviewed_at)

    def test_mark_changes_requested(self):
        """Test marking assignment as changes requested."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)
        assignment = ReviewerAssignment.objects.create(
            article=article,
            reviewer=self.reviewer1,
            assigned_by=self.admin,
        )

        assignment.mark_changes_requested(comment='Needs more detail.')

        assignment.refresh_from_db()
        self.assertEqual(
            assignment.status,
            ReviewerAssignment.AssignmentStatus.CHANGES_REQUESTED
        )
        self.assertEqual(assignment.review_comment, 'Needs more detail.')

    def test_reset_to_pending(self):
        """Test resetting assignment to pending."""
        article = self.create_article(status=Article.ArticleStatus.IN_REVIEW)
        assignment = ReviewerAssignment.objects.create(
            article=article,
            reviewer=self.reviewer1,
            assigned_by=self.admin,
            status=ReviewerAssignment.AssignmentStatus.APPROVED,
            reviewed_at=timezone.now(),
        )

        assignment.reset_to_pending()

        assignment.refresh_from_db()
        self.assertEqual(
            assignment.status,
            ReviewerAssignment.AssignmentStatus.PENDING
        )
        self.assertIsNone(assignment.reviewed_at)
