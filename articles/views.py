"""
Views for article management.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Article
from .forms import ArticleForm, ArticleSearchForm


class ArticleListView(ListView):
    """
    Public list of published articles.
    Accessible by all users (including anonymous).
    """
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        """Only show published articles, ordered by creation date."""
        queryset = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).select_related('author')

        # Handle search query
        search_query = self.request.GET.get('query')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add search form to context."""
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET or None)
        context['search_query'] = self.request.GET.get('query', '')
        return context


class ArticleDetailView(DetailView):
    """
    Article detail view - public for published articles.
    Increments view counter.
    """
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        """
        Authors can see their own drafts.
        Others can only see published articles.
        """
        queryset = Article.objects.select_related('author')

        if self.request.user.is_authenticated:
            # Authors can see their own articles (published or draft)
            return queryset.filter(
                Q(status=Article.ArticleStatus.PUBLISHED) |
                Q(author=self.request.user)
            )

        # Anonymous users only see published articles
        return queryset.filter(status=Article.ArticleStatus.PUBLISHED)

    def get_object(self, queryset=None):
        """Increment view counter when article is accessed."""
        obj = super().get_object(queryset)

        # Increment views (don't count author's own views)
        if not self.request.user == obj.author:
            obj.increment_views()

        return obj


class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure user is an author who has accepted rules.
    """

    def test_func(self):
        """Check if user is author and has accepted rules."""
        return (
            self.request.user.is_authenticated and
            self.request.user.is_author and
            self.request.user.has_accepted_rules
        )

    def handle_no_permission(self):
        """Custom handling for permission denied."""
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Please log in to access this page.')
            return redirect('users:login')

        if not self.request.user.is_author:
            messages.error(
                self.request,
                'Access denied. Only authors can create articles.'
            )
            return redirect('core:home')

        if not self.request.user.has_accepted_rules:
            messages.warning(
                self.request,
                'You must accept the article writing rules before creating articles.'
            )
            return redirect('users:accept_rules')

        return super().handle_no_permission()


class ArticleCreateView(AuthorRequiredMixin, CreateView):
    """
    Create new article - only for authors who accepted rules.
    """
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def form_valid(self, form):
        """Set the author before saving."""
        form.instance.author = self.request.user
        messages.success(
            self.request,
            f'Article "{form.instance.title}" created successfully!'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Display error message."""
        messages.error(
            self.request,
            'Failed to create article. Please correct the errors below.'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to article detail after creation."""
        return reverse_lazy('articles:detail', kwargs={'slug': self.object.slug})


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update article - only author can edit their own articles.
    """
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def test_func(self):
        """Only article author can edit."""
        article = self.get_object()
        return self.request.user == article.author

    def handle_no_permission(self):
        """Custom error message for permission denied."""
        messages.error(
            self.request,
            'Access denied. You can only edit your own articles.'
        )
        return redirect('articles:list')

    def form_valid(self, form):
        """Display success message."""
        messages.success(
            self.request,
            f'Article "{form.instance.title}" updated successfully!'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Display error message."""
        messages.error(
            self.request,
            'Failed to update article. Please correct the errors below.'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to article detail after update."""
        return reverse_lazy('articles:detail', kwargs={'slug': self.object.slug})


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete article - only author can delete their own articles.
    """
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('users:dashboard')

    def test_func(self):
        """Only article author can delete."""
        article = self.get_object()
        return self.request.user == article.author

    def handle_no_permission(self):
        """Custom error message for permission denied."""
        messages.error(
            self.request,
            'Access denied. You can only delete your own articles.'
        )
        return redirect('articles:list')

    def delete(self, request, *args, **kwargs):
        """Display success message on deletion."""
        article = self.get_object()
        messages.success(
            request,
            f'Article "{article.title}" has been deleted successfully.'
        )
        return super().delete(request, *args, **kwargs)


class MyArticlesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Author's own articles list (both draft and published).
    Only accessible by authors.
    """
    model = Article
    template_name = 'articles/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 12

    def test_func(self):
        """Only authors can access."""
        return self.request.user.is_author

    def handle_no_permission(self):
        """Redirect non-authors."""
        messages.error(
            self.request,
            'Access denied. This page is only for authors.'
        )
        return redirect('core:home')

    def get_queryset(self):
        """Get only current user's articles."""
        return Article.objects.filter(
            author=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add statistics to context."""
        context = super().get_context_data(**kwargs)
        user_articles = self.get_queryset()

        context['total_count'] = user_articles.count()
        context['published_count'] = user_articles.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).count()
        context['draft_count'] = user_articles.filter(
            status=Article.ArticleStatus.DRAFT
        ).count()

        return context
