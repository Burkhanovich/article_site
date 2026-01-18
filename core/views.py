"""
Core views for the platform.
Includes homepage, dashboard, and custom error pages.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from articles.models import Article


class HomeView(TemplateView):
    """
    Homepage view - shows recent published articles.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        """Add recent articles to context."""
        context = super().get_context_data(**kwargs)

        # Get latest published articles
        context['recent_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).select_related('author').order_by('-created_at')[:6]

        # Statistics
        context['total_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).count()

        return context


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view that redirects based on user role.
    Shows different content for authors and readers.
    """
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        """Add role-specific data to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_author:
            # Author statistics
            context['total_articles'] = Article.objects.filter(author=user).count()
            context['published_articles'] = Article.objects.filter(
                author=user,
                status=Article.ArticleStatus.PUBLISHED
            ).count()
            context['draft_articles'] = Article.objects.filter(
                author=user,
                status=Article.ArticleStatus.DRAFT
            ).count()
            context['recent_articles'] = Article.objects.filter(
                author=user
            ).order_by('-created_at')[:5]

            # Check if author has accepted rules
            context['has_accepted_rules'] = user.has_accepted_rules

        else:
            # Reader's recent viewed articles (all published)
            context['recent_articles'] = Article.objects.filter(
                status=Article.ArticleStatus.PUBLISHED
            ).select_related('author').order_by('-created_at')[:10]

        return context


# Custom Error Pages

def error_403(request, exception=None):
    """
    Custom 403 Forbidden error page.
    """
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    """
    Custom 404 Not Found error page.
    """
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """
    Custom 500 Internal Server Error page.
    """
    return render(request, 'errors/500.html', status=500)
