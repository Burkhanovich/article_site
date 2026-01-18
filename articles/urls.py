"""
URL configuration for articles app.
"""
from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Public article views
    path('', views.ArticleListView.as_view(), name='list'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),

    # Article management (authors only)
    path('create/new/', views.ArticleCreateView.as_view(), name='create'),
    path('<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='delete'),

    # Author's articles
    path('my/articles/', views.MyArticlesView.as_view(), name='my_articles'),
]
