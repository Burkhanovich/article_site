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

from .models import Article, Review
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

        if search_query:
            queryset = search_published_articles(search_query, lang)
        else:
            queryset = Article.objects.filter(
                status=Article.ArticleStatus.PUBLISHED
            )

        return queryset.select_related('author').prefetch_related(
            'keywords'
        ).order_by('-published_at', '-created_at').distinct()

    def get_context_data(self, **kwargs):
        """Add search form to context."""
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET or None)
        context['search_query'] = self.request.GET.get('query', '')
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
        ).prefetch_related('keywords', 'reviews__reviewer')

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
            elif self.request.user.is_staff or self.request.user.is_superuser or self.request.user.is_admin_user:
                can_view = True
            elif self.request.user.is_reviewer:
                # Reviewer can view if assigned to this article
                is_assigned = obj.reviewer_assignments.filter(
                    reviewer=self.request.user,
                ).exists()
                if is_assigned:
                    can_view = True

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
        if self.request.user.is_authenticated and article.can_be_reviewed:
            if self.request.user.is_reviewer or self.request.user.is_superuser:
                # Check if user is assigned to review this article
                is_assigned = article.reviewer_assignments.filter(
                    reviewer=self.request.user,
                    status='PENDING'
                ).exists()
                # Check if user hasn't already reviewed
                already_reviewed = article.reviews.filter(
                    reviewer=self.request.user
                ).exists()
                if is_assigned and not already_reviewed:
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
        from .workflow import ArticleWorkflow

        form.instance.author = self.request.user

        # Check if user wants to submit for admin review
        action = self.request.POST.get('action', 'save_draft')

        if action == 'submit_review':
            # First save as draft, then submit through workflow
            form.instance.status = Article.ArticleStatus.DRAFT
            response = super().form_valid(form)

            # Now submit through workflow (this handles notifications)
            success, message = ArticleWorkflow.submit_article(self.object, self.request.user)
            if success:
                messages.success(
                    self.request,
                    _('Article "%(title)s" has been submitted for admin review.') % {
                        'title': form.instance.title_uz
                    }
                )
            else:
                messages.warning(self.request, message)
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

    def get_initial(self):
        """Pre-select the journal matching the article's publication year/number."""
        from .models import Journal
        initial = super().get_initial()
        article = self.get_object()
        if article.publication_year and article.publication_number:
            journal = Journal.objects.filter(
                year=article.publication_year,
                number=article.publication_number,
            ).first()
            if journal:
                initial['journal'] = journal
        return initial

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
        from .workflow import ArticleWorkflow

        action = self.request.POST.get('action', 'save_draft')
        was_changes_requested = form.instance.status == Article.ArticleStatus.CHANGES_REQUESTED

        if action == 'submit_review':
            # Save changes first
            response = super().form_valid(form)

            # Check if this is a resubmission after changes requested
            if was_changes_requested:
                # Auto-publish on resubmission
                success, message = ArticleWorkflow.submit_and_auto_publish(self.object, self.request.user)
                if success:
                    messages.success(
                        self.request,
                        _('Article "%(title)s" has been published!') % {
                            'title': form.instance.title_uz
                        }
                    )
                else:
                    # Fallback to regular submission if auto-publish fails
                    success, message = ArticleWorkflow.submit_article(self.object, self.request.user)
                    if success:
                        messages.success(
                            self.request,
                            _('Article "%(title)s" has been resubmitted for review.') % {
                                'title': form.instance.title_uz
                            }
                        )
                    else:
                        messages.warning(self.request, message)
            else:
                # Regular submission from draft
                success, message = ArticleWorkflow.submit_article(self.object, self.request.user)
                if success:
                    messages.success(
                        self.request,
                        _('Article "%(title)s" has been submitted for admin review.') % {
                            'title': form.instance.title_uz
                        }
                    )
                else:
                    messages.warning(self.request, message)
            return response
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
        ).prefetch_related('keywords').order_by('-created_at')

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
        from .workflow import ArticleWorkflow

        article = get_object_or_404(Article, slug=slug)
        was_changes_requested = article.status == Article.ArticleStatus.CHANGES_REQUESTED

        if was_changes_requested:
            # Auto-publish on resubmission after changes requested
            success, message = ArticleWorkflow.submit_and_auto_publish(article, request.user)
            if success:
                messages.success(
                    request,
                    _('Article "%(title)s" has been published!') % {
                        'title': article.title_uz
                    }
                )
            else:
                messages.error(request, message)
        else:
            # Regular submission
            success, message = ArticleWorkflow.submit_article(article, request.user)
            if success:
                messages.success(
                    request,
                    _('Article "%(title)s" has been submitted for admin review.') % {
                        'title': article.title_uz
                    }
                )
            else:
                messages.error(request, message)

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
    """Dashboard for reviewers showing their assigned articles."""
    template_name = 'articles/reviewer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import ReviewerAssignment
        
        # Get all assignments for this reviewer
        user = self.request.user
        all_assignments = ReviewerAssignment.objects.filter(
            reviewer=user
        ).select_related('article', 'article__author').order_by('-assigned_at')
        
        # Separate by status
        pending_assignments = all_assignments.filter(status=ReviewerAssignment.AssignmentStatus.PENDING)
        reviewed_assignments = all_assignments.exclude(status=ReviewerAssignment.AssignmentStatus.PENDING)
        
        # Get counts by status
        status_counts = {
            'pending': pending_assignments.count(),
            'approved': all_assignments.filter(status=ReviewerAssignment.AssignmentStatus.APPROVED).count(),
            'changes': all_assignments.filter(status=ReviewerAssignment.AssignmentStatus.CHANGES_REQUESTED).count(),
            'rejected': all_assignments.filter(status=ReviewerAssignment.AssignmentStatus.REJECTED).count(),
        }
        
        context['pending_assignments'] = pending_assignments
        context['reviewed_assignments'] = reviewed_assignments
        context['pending_count'] = status_counts['pending']
        context['approved_count'] = status_counts['approved']
        context['changes_count'] = status_counts['changes']
        context['rejected_count'] = status_counts['rejected']
        context['reviewed_count'] = reviewed_assignments.count()
        context['total_assignments'] = all_assignments.count()

        return context


class ArticleReviewPageView(ReviewerRequiredMixin, DetailView):
    """
    Dedicated article review page for reviewers.
    Shows article content and review form.
    """
    model = Article
    template_name = 'articles/article_review.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        """Get article with permission check."""
        article = get_object_or_404(
            Article.objects.select_related('author').prefetch_related(
                'keywords'
            ),
            slug=self.kwargs['slug']
        )

        # Check if user is assigned to review this article
        is_assigned = article.reviewer_assignments.filter(
            reviewer=self.request.user,
        ).exists() or self.request.user.is_superuser

        if not is_assigned:
            messages.error(self.request, _('You are not assigned to review this article.'))
            raise Http404(_("Article not available for review."))

        return article

    def get_context_data(self, **kwargs):
        from .models import ReviewerAssignment
        
        context = super().get_context_data(**kwargs)
        article = self.object
        lang = get_language() or 'uz'

        # Get title and content in current language
        context['title'] = article.get_title(lang)
        context['content'] = article.get_content(lang)

        # Check if already reviewed
        existing_review = article.reviewer_assignments.filter(
            reviewer=self.request.user
        ).exclude(status=ReviewerAssignment.AssignmentStatus.PENDING).first()

        context['existing_review'] = existing_review
        context['can_review'] = not existing_review
        context['form'] = None if existing_review else ReviewForm()

        return context


class SubmitReviewView(ReviewerRequiredMixin, View):
    """Submit a review for an article."""

    def post(self, request, slug):
        """Handle review submission."""
        article = get_object_or_404(Article, slug=slug)

        # Verify reviewer is assigned to this article
        is_assigned = article.reviewer_assignments.filter(
            reviewer=request.user,
        ).exists() or request.user.is_superuser

        if not is_assigned:
            messages.error(request, _('You are not assigned to review this article.'))
            return redirect('articles:detail', slug=slug)

        # Check for existing review
        existing = Review.objects.filter(
            article=article,
            reviewer=request.user
        ).exists()

        if existing:
            messages.warning(request, _('You have already reviewed this article.'))
            return redirect('articles:detail', slug=slug)

        form = ReviewForm(request.POST)
        form.instance.article = article
        form.instance.reviewer = request.user

        if form.is_valid():
            # Save the Review object — the post_save signal
            # triggers process_review_result() which handles:
            #   - ReviewerAssignment sync
            #   - Article status update
            #   - Author notification + email
            #   - Admin notification + email
            form.save()
            messages.success(request, _('Your review has been submitted.'))
        else:
            for error in form.errors.values():
                messages.error(request, error)

        # Redirect back to review page or article detail
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('articles:detail', slug=slug)

