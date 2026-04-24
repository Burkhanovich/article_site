"""
Tests for admin panel functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from articles.models import Article, Review, ReviewerAssignment
from users.models import CustomUser

User = get_user_model()


class AdminAccessTestCase(TestCase):
    """Test admin panel access control."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.reviewer_user = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123',
            role=CustomUser.UserRole.REVIEWER
        )
        self.author_user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            role=CustomUser.UserRole.AUTHOR
        )
    
    def test_admin_can_access_dashboard(self):
        """Test admin user can access admin dashboard."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/dashboard.html')
    
    def test_reviewer_cannot_access_admin_panel(self):
        """Test reviewer user is redirected from admin panel."""
        self.client.login(username='reviewer', password='testpass123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_author_cannot_access_admin_panel(self):
        """Test author user is redirected from admin panel."""
        self.client.login(username='author', password='testpass123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_anonymous_user_cannot_access_admin_panel(self):
        """Test anonymous users are redirected."""
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertNotEqual(response.status_code, 200)


class ReviewerManagementTestCase(TestCase):
    """Test reviewer management functionality."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.client.login(username='admin', password='testpass123')
    
    def test_create_reviewer(self):
        """Test creating a new reviewer."""
        data = {
            'username': 'newreviewer',
            'email': 'newreviewer@test.com',
            'first_name': 'Test',
            'last_name': 'Reviewer',
            'organization': 'Test Org',
            'password1': 'securepass123',
            'password2': 'securepass123',
        }
        response = self.client.post(reverse('admin_panel:reviewer_create'), data)
        
        # Check reviewer was created
        self.assertTrue(User.objects.filter(username='newreviewer').exists())
        new_reviewer = User.objects.get(username='newreviewer')
        self.assertEqual(new_reviewer.role, CustomUser.UserRole.REVIEWER)
    
    def test_list_reviewers(self):
        """Test listing all reviewers."""
        User.objects.create_user(
            username='reviewer1',
            email='reviewer1@test.com',
            password='testpass123',
            role=CustomUser.UserRole.REVIEWER
        )
        
        response = self.client.get(reverse('admin_panel:reviewer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'reviewer1')
    
    def test_edit_reviewer(self):
        """Test editing reviewer details."""
        reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123',
            role=CustomUser.UserRole.REVIEWER,
            first_name='Old'
        )
        
        data = {
            'username': 'reviewer',
            'email': 'newemail@test.com',
            'first_name': 'New',
            'last_name': 'Name',
            'organization': 'New Org',
            'is_active': True
        }
        response = self.client.post(
            reverse('admin_panel:reviewer_edit', kwargs={'pk': reviewer.pk}),
            data
        )
        
        reviewer.refresh_from_db()
        self.assertEqual(reviewer.first_name, 'New')
        self.assertEqual(reviewer.email, 'newemail@test.com')


class ArticleManagementTestCase(TestCase):
    """Test article management functionality."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            role=CustomUser.UserRole.AUTHOR
        )
        self.article = Article.objects.create(
            title_uz='Test Article',
            title_ru='Тестовая статья',
            title_en='Test Article',
            content_uz='Test content',
            author=self.author,
            status=Article.ArticleStatus.PENDING_ADMIN
        )
        self.client.login(username='admin', password='testpass123')
    
    def test_list_articles(self):
        """Test listing articles."""
        response = self.client.get(reverse('admin_panel:article_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
    
    def test_filter_articles_by_status(self):
        """Test filtering articles by status."""
        response = self.client.get(
            reverse('admin_panel:article_manage'),
            {'status': Article.ArticleStatus.PENDING_ADMIN}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
    
    def test_publish_article(self):
        """Test publishing an article."""
        data = {
            'action': 'publish',
            'note': ''
        }
        response = self.client.post(
            reverse('admin_panel:article_action',
                   kwargs={'slug': self.article.slug}),
            data
        )
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, Article.ArticleStatus.PUBLISHED)
        self.assertEqual(self.article.admin_decision_by, self.admin_user)
    
    def test_reject_article(self):
        """Test rejecting an article."""
        data = {
            'action': 'reject',
            'note': 'This article does not meet standards.'
        }
        response = self.client.post(
            reverse('admin_panel:article_action',
                   kwargs={'slug': self.article.slug}),
            data
        )
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, Article.ArticleStatus.REJECTED)
        self.assertEqual(self.article.admin_note, 'This article does not meet standards.')
    
    def test_request_changes(self):
        """Test requesting changes on an article."""
        data = {
            'action': 'request_changes',
            'note': 'Please revise the conclusion.'
        }
        response = self.client.post(
            reverse('admin_panel:article_action',
                   kwargs={'slug': self.article.slug}),
            data
        )
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, Article.ArticleStatus.CHANGES_REQUESTED)

    def test_assign_reviewer_from_action_view(self):
        """Test assigning reviewers via the article action view."""
        reviewer = User.objects.create_user(
            username='assign-reviewer',
            email='assign@test.com',
            password='testpass123',
            role=CustomUser.UserRole.REVIEWER
        )

        response = self.client.post(
            reverse('admin_panel:article_action', kwargs={'slug': self.article.slug}),
            {
                'assign_reviewers': '1',
                'reviewers': [str(reviewer.pk)],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ReviewerAssignment.objects.filter(article=self.article, reviewer=reviewer).exists()
        )


class DashboardTestCase(TestCase):
    """Test admin dashboard functionality."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.client.login(username='admin', password='testpass123')
    
    def test_dashboard_has_statistics(self):
        """Test dashboard displays statistics."""
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check for statistics in context
        self.assertIn('total_articles', response.context)
        self.assertIn('total_reviewers', response.context)
        self.assertIn('total_journals', response.context)


class AdminLoginRedirectTestCase(TestCase):
    """Test that admin users are redirected to admin panel on login."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_login_test',
            email='admin_login@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.author_user = User.objects.create_user(
            username='author_login_test',
            email='author_login@test.com',
            password='testpass123',
            role=CustomUser.UserRole.AUTHOR
        )
        self.login_url = reverse('users:login')
    
    def test_admin_redirected_to_admin_panel_on_login(self):
        """Test that admin users are redirected to admin panel after login."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'admin_login_test',
                'password': 'testpass123'
            },
            follow=True
        )
        
        # Check that final URL is admin panel
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any('admin-panel' in str(url[0]) for url in response.redirect_chain),
            f"Expected redirect to admin panel, got: {response.redirect_chain}"
        )
    
    def test_author_not_redirected_to_admin_panel(self):
        """Test that non-admin users are not redirected to admin panel."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'author_login_test',
                'password': 'testpass123'
            },
            follow=True
        )
        
        # Check that final URL is NOT admin panel
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            any('admin-panel' in str(url[0]) for url in response.redirect_chain),
            f"Author should not be redirected to admin panel, got: {response.redirect_chain}"
        )


class AdminDashboardViewTestCase(TestCase):
    """Test that admin users see appropriate dashboard content."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_dashboard_test',
            email='admin_dash@test.com',
            password='testpass123',
            role=CustomUser.UserRole.ADMIN
        )
        self.author_user = User.objects.create_user(
            username='author_dashboard_test',
            email='author_dash@test.com',
            password='testpass123',
            role=CustomUser.UserRole.AUTHOR,
            has_accepted_rules=True
        )
    
    def test_admin_dashboard_shows_admin_options(self):
        """Test that admin users see admin-specific dashboard content."""
        self.client.login(username='admin_dashboard_test', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        # Should show admin panel buttons
        self.assertContains(response, 'Admin Panel')
        self.assertContains(response, 'Manage Reviewers')
        self.assertContains(response, 'Manage Articles')
        self.assertContains(response, 'Jurnallarni boshqarish')
    
    def test_author_dashboard_does_not_show_admin_options(self):
        """Test that author users don't see admin options."""
        self.client.login(username='author_dashboard_test', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        # Should NOT show admin panel access
        self.assertNotContains(response, 'Admin Dashboard')
        # Should show author dashboard (check for statistics cards)
        self.assertContains(response, 'Jami maqolalar')
    
    def test_admin_home_shows_admin_notification(self):
        """Test that admin users see admin notification on home page."""
        self.client.login(username='admin_dashboard_test', password='testpass123')
        response = self.client.get(reverse('core:home'))
        
        self.assertEqual(response.status_code, 200)
        # Should show admin notification
        self.assertContains(response, 'Admin Account')
        self.assertContains(response, 'Go to Admin Panel')
