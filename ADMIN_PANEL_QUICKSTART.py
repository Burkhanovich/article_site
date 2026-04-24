"""
Admin Panel Quick Start Guide

This script shows typical commands and workflows to get started with the admin panel.
"""

# ============================================================================
# STEP 1: Create Admin User
# ============================================================================

# Run Django shell:
# python manage.py shell

from users.models import CustomUser

# Create admin user
admin_user = CustomUser.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='secure_password_here',  # Change this!
    role=CustomUser.UserRole.ADMIN,
    first_name='Admin',
    last_name='User',
    is_staff=True,
    is_superuser=True
)

# Verify creation
print(f"Created admin user: {admin_user}")


# ============================================================================
# STEP 2: Create Test Reviewers
# ============================================================================

# Create multiple reviewers
reviewers = []
for i in range(3):
    reviewer = CustomUser.objects.create_user(
        username=f'reviewer{i+1}',
        email=f'reviewer{i+1}@example.com',
        password='reviewerpass123',
        role=CustomUser.UserRole.REVIEWER,
        first_name=f'Reviewer {i+1}',
        organization='Editorial Board'
    )
    reviewers.append(reviewer)
    print(f"Created reviewer: {reviewer.username}")


# ============================================================================
# STEP 3: Access Admin Panel
# ============================================================================

# Start Django development server:
# python manage.py runserver

# Then navigate to:
# http://localhost:8000/uz/admin-panel/
# (or replace 'uz' with 'ru' or 'en' for other languages)

# Login with:
# Username: admin
# Password: secure_password_here


# ============================================================================
# STEP 4: Assign Reviewers to Categories
# ============================================================================

# Using Django shell:
from articles.models import Category

# Get a category
category = Category.objects.first()

# Assign reviewers
for reviewer in reviewers:
    category.reviewers.add(reviewer)

print(f"Assigned {category.reviewers.count()} reviewers to {category.name_uz}")


# ============================================================================
# STEP 5: Configure Category Policy
# ============================================================================

from articles.models import CategoryPolicy

# Get or create policy
policy, created = CategoryPolicy.objects.get_or_create(category=category)

# Configure policy settings
policy.min_approvals_to_publish = 2
policy.min_required_reviews = 2
policy.max_rejections_before_block = 1
policy.review_deadline_hours = 72
policy.allow_admin_override = True
policy.require_changes_comment = True
policy.require_reject_comment = True
policy.save()

print(f"Configured policy for {category.name_uz}")


# ============================================================================
# STEP 6: Create Test Articles
# ============================================================================

from articles.models import Article
from users.models import CustomUser

# Create an author
author = CustomUser.objects.create_user(
    username='author1',
    email='author1@example.com',
    password='authorpass123',
    role=CustomUser.UserRole.AUTHOR,
    first_name='Test',
    last_name='Author'
)

# Create a test article
article = Article.objects.create(
    title_uz='Test Article',
    title_ru='Тестовая статья',
    title_en='Test Article',
    content_uz='This is test content for the article.',
    author=author,
    status=Article.ArticleStatus.PENDING_ADMIN
)
article.categories.add(category)

print(f"Created article: {article.title_uz}")


# ============================================================================
# COMMON ADMIN TASKS IN SHELL
# ============================================================================

# Get all reviewers
reviewers = CustomUser.objects.filter(role=CustomUser.UserRole.REVIEWER)

# Get pending articles
pending = Article.objects.filter(status=Article.ArticleStatus.PENDING_ADMIN)

# Get reviewers for a category
cat_reviewers = category.reviewers.all()

# Get articles for a category
cat_articles = category.articles.all()

# Get reviews for an article
article_reviews = article.reviews.all()

# Count articles by status
from django.db.models import Count
status_counts = Article.objects.values('status').annotate(count=Count('id'))

# Get reviewer statistics
reviewer_stats = CustomUser.objects.filter(
    role=CustomUser.UserRole.REVIEWER
).annotate(
    review_count=Count('reviews'),
    category_count=Count('assigned_categories')
)


# ============================================================================
# HELPFUL URLS
# ============================================================================

"""
Once you've set up the admin panel, here are the URLs you can visit:

Admin Panel:
- http://localhost:8000/uz/admin-panel/

Reviewer Management:
- http://localhost:8000/uz/admin-panel/reviewers/            (List)
- http://localhost:8000/uz/admin-panel/reviewers/create/     (Create)
- http://localhost:8000/uz/admin-panel/reviewers/1/          (View)
- http://localhost:8000/uz/admin-panel/reviewers/1/edit/     (Edit)
- http://localhost:8000/uz/admin-panel/reviewers/1/delete/   (Delete)

Category Management:
- http://localhost:8000/uz/admin-panel/categories/                    (List)
- http://localhost:8000/uz/admin-panel/categories/1/assign-reviewers/ (Assign)
- http://localhost:8000/uz/admin-panel/categories/1/policy/           (Policy)

Article Management:
- http://localhost:8000/uz/admin-panel/articles/              (List)
- http://localhost:8000/uz/admin-panel/articles/slug/action/  (Action)
- http://localhost:8000/uz/admin-panel/articles/bulk-action/  (Bulk)

System:
- http://localhost:8000/uz/admin-panel/statistics/            (Stats)
"""


# ============================================================================
# TESTING THE ADMIN PANEL
# ============================================================================

"""
Run tests with:
    python manage.py test admin_panel

Run specific test class:
    python manage.py test admin_panel.tests.AdminAccessTestCase

Run specific test method:
    python manage.py test admin_panel.tests.AdminAccessTestCase.test_admin_can_access_dashboard

Verbose output:
    python manage.py test admin_panel -v 2
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: Can't see Admin Panel link in navbar
Solution: Make sure you're logged in as admin user (role='ADMIN' or is_superuser=True)

Problem: Form submission redirects to login
Solution: Make sure CSRF token is in form, check browser cookie settings

Problem: Reviewers not showing in dropdown
Solution: Make sure reviewers have role='REVIEWER' and is_active=True

Problem: Articles not filtering
Solution: Make sure article status matches exactly (e.g., 'PENDING_ADMIN' not 'pending')

Problem: Categories not showing reviewers
Solution: Need to use category.reviewers.add(user) to assign reviewers

Problem: Changes not appearing
Solution: Do a hard refresh (Ctrl+Shift+R) to clear cache
"""


# ============================================================================
# USEFUL QUERYSETS
# ============================================================================

"""
# Get all pending articles with author info
pending = Article.objects.filter(
    status=Article.ArticleStatus.PENDING_ADMIN
).select_related('author')

# Get reviewers with their article count
reviewers = CustomUser.objects.filter(
    role=CustomUser.UserRole.REVIEWER
).annotate(review_count=Count('reviews'))

# Get categories with reviewer count
categories = Category.objects.annotate(
    reviewer_count=Count('reviewers'),
    article_count=Count('articles')
)

# Get articles with review count and status
articles = Article.objects.annotate(
    review_count=Count('reviews')
).select_related('author')

# Get articles in review with reviews
in_review = Article.objects.filter(
    status=Article.ArticleStatus.IN_REVIEW
).prefetch_related('reviews__reviewer')

# Get reviewer performance statistics
reviewers = CustomUser.objects.filter(
    role=CustomUser.UserRole.REVIEWER
).annotate(
    total_reviews=Count('reviews'),
    approved=Count('reviews', filter=Q(reviews__decision='APPROVED')),
    rejected=Count('reviews', filter=Q(reviews__decision='REJECTED')),
    changes=Count('reviews', filter=Q(reviews__decision='CHANGES_REQUESTED'))
)
"""


# ============================================================================
# ADMIN ACTIONS VIA SHELL
# ============================================================================

# Publish an article
article.status = Article.ArticleStatus.PUBLISHED
article.admin_decision_by = admin_user
article.published_at = timezone.now()
article.save()

# Reject an article
article.status = Article.ArticleStatus.REJECTED
article.admin_note = "Article does not meet publication standards"
article.admin_decision_by = admin_user
article.save()

# Request changes
article.status = Article.ArticleStatus.CHANGES_REQUESTED
article.admin_note = "Please revise the conclusion section"
article.admin_decision_by = admin_user
article.save()

# Reset article
article.status = Article.ArticleStatus.IN_REVIEW
article.save()


print("""
✅ Admin Panel is ready to use!

Next steps:
1. Start Django: python manage.py runserver
2. Go to: http://localhost:8000/uz/admin-panel/
3. Login with admin credentials
4. Create reviewers and assign categories
5. Configure category policies
6. Manage articles and reviews

For more help, see:
- ADMIN_PANEL_SETUP.md
- ADMIN_PANEL_COMPLETE.md
- admin_panel/README.md
""")
