"""
Views for article management with editorial workflow.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, get_language
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)

from .models import Article, Category, Review
from .forms import ArticleForm, ArticleSearchForm, ReviewForm
from .services import is_article_publishable, get_reviewer_queue, search_published_articles


class ArticleListView(ListView):
    """
    Public list of published articles only.
    Readers can only see PUBLISHED articles.
    """
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        """Only show PUBLISHED articles, ordered by creation date."""
        lang = get_language() or 'uz'
        search_query = self.request.GET.get('query')
        category_id = self.request.GET.get('category')

        if search_query:
            queryset = search_published_articles(search_query, lang)
        else:
            queryset = Article.objects.filter(
                status=Article.ArticleStatus.PUBLISHED
            )

        # Filter by category if specified
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        return queryset.select_related('author').prefetch_related(
            'categories', 'keywords'
        ).order_by('-published_at', '-created_at').distinct()

    def get_context_data(self, **kwargs):
        """Add search form and categories to context."""
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET or None)
        context['search_query'] = self.request.GET.get('query', '')
        context['categories'] = Category.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ArticleDetailView(DetailView):
    """
    Article detail view with access control:
    - PUBLISHED articles: visible to everyone
    - Other statuses: visible only to author OR staff/admin/reviewer
    """
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        """Build queryset based on user permissions."""
        return Article.objects.select_related(
            'author', 'admin_decision_by'
        ).prefetch_related('categories', 'keywords', 'reviews__reviewer')

    def get_object(self, queryset=None):
        """Get article with permission check."""
        obj = super().get_object(queryset)

        # Check access permissions
        can_view = False

        if obj.status == Article.ArticleStatus.PUBLISHED:
            can_view = True
        elif self.request.user.is_authenticated:
            if self.request.user == obj.author:
                can_view = True
            elif self.request.user.is_staff or self.request.user.is_superuser:
                can_view = True
            elif self.request.user.is_reviewer:
                # Reviewer can view if article is in review and in their category
                if obj.can_be_reviewed:
                    for cat in obj.categories.all():
                        if self.request.user.can_review_category(cat):
                            can_view = True
                            break

        if not can_view:
            raise Http404(_("Article not found."))

        # Increment views (don't count author's own views)
        if self.request.user != obj.author:
            obj.increment_views()

        return obj

    def get_context_data(self, **kwargs):
        """Add extra context for template."""
        context = super().get_context_data(**kwargs)
        article = self.object
        lang = get_language() or 'uz'

        # Get title and content in current language
        context['title'] = article.get_title(lang)
        context['content'] = article.get_content(lang)

        # Determine if user can edit this article
        context['can_edit'] = (
            self.request.user.is_authenticated and
            self.request.user == article.author and
            article.can_be_edited_by_author
        )

        # Determine if user can submit for review
        context['can_submit'] = (
            self.request.user.is_authenticated and
            self.request.user == article.author and
            article.is_draft
        )

        # Determine if user can review
        context['can_review'] = False
        context['reviewable_categories'] = []
        if self.request.user.is_authenticated and article.can_be_reviewed:
            if self.request.user.is_reviewer or self.request.user.is_superuser:
                for cat in article.categories.all():
                    if self.request.user.can_review_category(cat):
                        # Check if user hasn't already reviewed this category
                        existing = article.reviews.filter(
                            reviewer=self.request.user,
                            category=cat
                        ).exists()
                        if not existing:
                            context['reviewable_categories'].append(cat)
                            context['can_review'] = True

        # Get publishability info for admins
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            context['publishability'] = is_article_publishable(article)

        return context


class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure user is an author.
    """

    def test_func(self):
        """Check if user can create articles."""
        return (
            self.request.user.is_authenticated and
            self.request.user.can_create_articles
        )

    def handle_no_permission(self):
        """Custom handling for permission denied."""
        if not self.request.user.is_authenticated:
            messages.error(self.request, _('Please log in to access this page.'))
            return redirect('users:login')

        messages.error(
            self.request,
            _('Access denied. Only authors can create articles.')
        )
        return redirect('core:home')


class ArticleCreateView(AuthorRequiredMixin, CreateView):
    """
    Create new article - only for authors.
    New articles start as DRAFT by default.
    """
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def form_valid(self, form):
        """Set the author and handle submission action."""
        form.instance.author = self.request.user

        # Check if user wants to submit for admin review
        action = self.request.POST.get('action', 'save_draft')

        if action == 'submit_review':
            form.instance.status = Article.ArticleStatus.PENDING_ADMIN
            from django.utils import timezone
            form.instance.submitted_at = timezone.now()
            response = super().form_valid(form)
            messages.success(
                self.request,
                _('Article "%(title)s" has been submitted for admin review.') % {
                    'title': form.instance.title_uz
                }
            )
            return response
        else:
            form.instance.status = Article.ArticleStatus.DRAFT
            response = super().form_valid(form)
            messages.success(
                self.request,
                _('Article "%(title)s" saved as draft.') % {'title': form.instance.title_uz}
            )
            return response

    def form_invalid(self, form):
        """Display error message."""
        messages.error(
            self.request,
            _('Failed to create article. Please correct the errors below.')
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to article detail after creation."""
        return reverse_lazy('articles:detail', kwargs={'slug': self.object.slug})


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update article - only author can edit their own articles.
    Can only edit DRAFT or CHANGES_REQUESTED articles.
    """
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def test_func(self):
        """Only article author can edit, and only editable articles."""
        article = self.get_object()
        return (
            self.request.user == article.author and
            article.can_be_edited_by_author
        )

    def handle_no_permission(self):
        """Custom error message for permission denied."""
        if not self.request.user.is_authenticated:
            messages.error(self.request, _('Please log in to edit articles.'))
            return redirect('users:login')

        article = self.get_object()
        if self.request.user != article.author:
            messages.error(
                self.request,
                _('Access denied. You can only edit your own articles.')
            )
        elif not article.can_be_edited_by_author:
            messages.error(
                self.request,
                _('This article cannot be edited in its current status.')
            )
        return redirect('articles:my_articles')

    def form_valid(self, form):
        """Handle save action (draft or submit for review)."""
        action = self.request.POST.get('action', 'save_draft')

        if action == 'submit_review':
            form.instance.submit_to_admin()
            messages.success(
                self.request,
                _('Article "%(title)s" has been submitted for admin review.') % {
                    'title': form.instance.title_uz
                }
            )
        else:
            form.instance.status = Article.ArticleStatus.DRAFT
            messages.success(
                self.request,
                _('Article "%(title)s" updated and saved as draft.') % {
                    'title': form.instance.title_uz
                }
            )

        return super().form_valid(form)

    def form_invalid(self, form):
        """Display error message."""
        messages.error(
            self.request,
            _('Failed to update article. Please correct the errors below.')
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
    success_url = reverse_lazy('articles:my_articles')

    def test_func(self):
        """Only article author can delete."""
        article = self.get_object()
        return self.request.user == article.author

    def handle_no_permission(self):
        """Custom error message for permission denied."""
        messages.error(
            self.request,
            _('Access denied. You can only delete your own articles.')
        )
        return redirect('articles:list')

    def delete(self, request, *args, **kwargs):
        """Display success message on deletion."""
        article = self.get_object()
        messages.success(
            request,
            _('Article "%(title)s" has been deleted successfully.') % {
                'title': article.title_uz
            }
        )
        return super().delete(request, *args, **kwargs)


class MyArticlesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Author's own articles list (all statuses).
    Only accessible by authors.
    """
    model = Article
    template_name = 'articles/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 12

    def test_func(self):
        """Only authors can access."""
        return self.request.user.can_create_articles

    def handle_no_permission(self):
        """Redirect non-authors."""
        messages.error(
            self.request,
            _('Access denied. This page is only for authors.')
        )
        return redirect('core:home')

    def get_queryset(self):
        """Get only current user's articles."""
        queryset = Article.objects.filter(
            author=self.request.user
        ).prefetch_related('categories', 'keywords').order_by('-created_at')

        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter in dict(Article.ArticleStatus.choices):
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add statistics to context."""
        context = super().get_context_data(**kwargs)
        user_articles = Article.objects.filter(author=self.request.user)

        context['total_count'] = user_articles.count()
        context['published_count'] = user_articles.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).count()
        context['draft_count'] = user_articles.filter(
            status=Article.ArticleStatus.DRAFT
        ).count()
        context['pending_admin_count'] = user_articles.filter(
            status=Article.ArticleStatus.PENDING_ADMIN
        ).count()
        context['in_review_count'] = user_articles.filter(
            status=Article.ArticleStatus.IN_REVIEW
        ).count()
        context['changes_requested_count'] = user_articles.filter(
            status=Article.ArticleStatus.CHANGES_REQUESTED
        ).count()
        context['rejected_count'] = user_articles.filter(
            status=Article.ArticleStatus.REJECTED
        ).count()

        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Article.ArticleStatus.choices

        return context


class SubmitArticleView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Submit article for admin review.
    Only author can submit their own DRAFT or CHANGES_REQUESTED articles.
    """

    def test_func(self):
        """Check user can submit this article."""
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        return (
            self.request.user == article.author and
            article.status in [Article.ArticleStatus.DRAFT, Article.ArticleStatus.CHANGES_REQUESTED]
        )

    def handle_no_permission(self):
        """Custom error message for permission denied."""
        messages.error(
            self.request,
            _('You cannot submit this article for review.')
        )
        return redirect('articles:my_articles')

    def post(self, request, slug):
        """Handle article submission."""
        article = get_object_or_404(Article, slug=slug)

        if article.submit_to_admin():
            messages.success(
                request,
                _('Article "%(title)s" has been submitted for admin review.') % {
                    'title': article.title_uz
                }
            )
        else:
            messages.error(
                request,
                _('This article cannot be submitted for review.')
            )

        return redirect('articles:detail', slug=slug)


# Reviewer Views

class ReviewerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is a reviewer."""

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            (self.request.user.is_reviewer or self.request.user.is_superuser)
        )

    def handle_no_permission(self):
        messages.error(self.request, _('Access denied. Reviewers only.'))
        return redirect('core:home')


class ReviewerDashboardView(ReviewerRequiredMixin, TemplateView):
    """Dashboard for reviewers showing their review queue."""
    template_name = 'articles/reviewer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queue'] = get_reviewer_queue(self.request.user)

        # Recent reviews by this user
        context['recent_reviews'] = Review.objects.filter(
            reviewer=self.request.user
        ).select_related('article', 'category').order_by('-created_at')[:10]

        return context


class ArticleReviewPageView(ReviewerRequiredMixin, DetailView):
    """
    Dedicated article review page for reviewers.
    Shows article content and review form for each assigned category.
    """
    model = Article
    template_name = 'articles/article_review.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        """Get article with permission check."""
        article = get_object_or_404(
            Article.objects.select_related('author').prefetch_related(
                'categories', 'keywords', 'reviews__reviewer', 'reviews__category'
            ),
            slug=self.kwargs['slug']
        )

        # Check if article can be reviewed
        if not article.can_be_reviewed:
            messages.error(self.request, _('This article cannot be reviewed in its current status.'))
            raise Http404(_("Article not available for review."))

        # Check if user can review at least one category
        can_review_any = False
        for cat in article.categories.all():
            if self.request.user.can_review_category(cat):
                can_review_any = True
                break

        if not can_review_any and not self.request.user.is_superuser:
            messages.error(self.request, _('You are not assigned to review any category of this article.'))
            raise Http404(_("Article not available for review."))

        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        lang = get_language() or 'uz'

        # Get title and content in current language
        context['title'] = article.get_title(lang)
        context['content'] = article.get_content(lang)

        # Get reviewable categories with their review forms
        reviewable_categories = []
        for category in article.categories.all():
            if self.request.user.can_review_category(category) or self.request.user.is_superuser:
                existing_review = article.reviews.filter(
                    reviewer=self.request.user,
                    category=category
                ).first()

                reviewable_categories.append({
                    'category': category,
                    'existing_review': existing_review,
                    'form': ReviewForm(category=category) if not existing_review else None,
                })

        context['reviewable_categories'] = reviewable_categories

        # Get all existing reviews for this article (grouped by category)
        context['all_reviews'] = article.reviews.select_related(
            'reviewer', 'category'
        ).order_by('category__name_uz', '-created_at')

        return context


class SubmitReviewView(ReviewerRequiredMixin, View):
    """Submit a review for an article in a specific category."""

    def post(self, request, slug, category_id):
        """Handle review submission."""
        from users.services import notify_review_submitted

        article = get_object_or_404(Article, slug=slug)
        category = get_object_or_404(Category, id=category_id)

        # Verify reviewer can review this category
        if not request.user.can_review_category(category):
            messages.error(request, _('You are not assigned to review this category.'))
            return redirect('articles:detail', slug=slug)

        # Verify article has this category
        if not article.categories.filter(pk=category.pk).exists():
            messages.error(request, _('Article does not belong to this category.'))
            return redirect('articles:detail', slug=slug)

        # Verify article is reviewable
        if not article.can_be_reviewed:
            messages.error(request, _('This article cannot be reviewed in its current status.'))
            return redirect('articles:detail', slug=slug)

        # Check for existing review
        existing = Review.objects.filter(
            article=article,
            reviewer=request.user,
            category=category
        ).exists()

        if existing:
            messages.warning(request, _('You have already reviewed this article for this category.'))
            return redirect('articles:detail', slug=slug)

        form = ReviewForm(request.POST, category=category)
        form.instance.article = article
        form.instance.reviewer = request.user
        form.instance.category = category

        if form.is_valid():
            review = form.save()


            # Update article status if needed
            from .services import update_article_status_from_reviews
            update_article_status_from_reviews(article)

            # Send notification to author
            notify_review_submitted(article.author, article, review, request.user)

            messages.success(request, _('Your review has been submitted.'))
        else:
            for error in form.errors.values():
                messages.error(request, error)

        # Redirect back to review page or article detail
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('articles:detail', slug=slug)


class CategoryArticlesView(ListView):
    """List articles in a specific category."""
    model = Article
    template_name = 'articles/category_articles.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            categories=self.category
        ).select_related('author').prefetch_related('keywords').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
