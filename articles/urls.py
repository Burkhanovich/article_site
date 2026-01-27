"""
URL configuration for articles app.
"""
from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Public article views
    path('', views.ArticleListView.as_view(), name='list'),

    # Author's articles (before slug patterns)
    path('my/articles/', views.MyArticlesView.as_view(), name='my_articles'),

    # Article management (authors only)
    path('create/new/', views.ArticleCreateView.as_view(), name='create'),

    # Reviewer dashboard and review page
    path('reviewer/dashboard/', views.ReviewerDashboardView.as_view(), name='reviewer_dashboard'),
    path('reviewer/article/<slug:slug>/', views.ArticleReviewPageView.as_view(), name='article_review'),

    # Category articles
    path('category/<slug:slug>/', views.CategoryArticlesView.as_view(), name='category_articles'),

    # Article detail and actions (slug-based - must be after specific paths)
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='delete'),
    path('<slug:slug>/submit/', views.SubmitArticleView.as_view(), name='submit'),

    # Review submission
    path('<slug:slug>/review/<int:category_id>/', views.SubmitReviewView.as_view(), name='submit_review'),
]
