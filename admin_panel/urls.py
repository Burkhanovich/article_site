"""
URL configuration for admin panel.
"""
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Reviewer Management
    path('reviewers/', views.ReviewerListView.as_view(), name='reviewer_list'),
    path('reviewers/create/', views.ReviewerCreateView.as_view(), name='reviewer_create'),
    path('reviewers/<int:pk>/', views.ReviewerDetailView.as_view(), name='reviewer_detail'),
    path('reviewers/<int:pk>/edit/', views.ReviewerEditView.as_view(), name='reviewer_edit'),
    path('reviewers/<int:pk>/delete/', views.ReviewerDeleteView.as_view(), name='reviewer_delete'),
    
    # Article Management
    path('articles/', views.ArticleManageView.as_view(), name='article_manage'),
    path('articles/<slug:slug>/action/', views.ArticleActionView.as_view(), name='article_action'),
    path('articles/bulk-action/', views.BulkArticleActionView.as_view(), name='bulk_article_action'),
    
    # System Statistics
    path('statistics/', views.SystemStatsView.as_view(), name='system_stats'),
    
    # Journal Management
    path('journals/', views.JournalListView.as_view(), name='journal_list'),
    path('journals/create/', views.JournalCreateView.as_view(), name='journal_create'),
    path('journals/<int:pk>/edit/', views.JournalUpdateView.as_view(), name='journal_edit'),
    path('journals/<int:pk>/deactivate/', views.JournalDeactivateView.as_view(), name='journal_deactivate'),
]
