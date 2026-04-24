"""
Views for admin control panel.
Manage reviewers, categories, article status, and system settings.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.views import View

from articles.models import Article, Review, Journal, ReviewerAssignment
from articles.workflow import ArticleWorkflow
from users.models import CustomUser
from .forms import (
    ReviewerCreationForm, ReviewerEditForm,
    ArticleActionForm, ReviewerAssignmentForm,
    BulkArticleActionForm, JournalForm
)

User = get_user_model()


class AdminAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admins can access the panel."""
    
    def test_func(self):
        return self.request.user.is_admin_user or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, _('You do not have permission to access the admin panel.'))
        return redirect('core:home')


class AdminDashboardView(AdminAccessMixin, TemplateView):
    """Admin dashboard with overview statistics."""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Article statistics
        context['total_articles'] = Article.objects.count()
        context['draft_articles'] = Article.objects.filter(status=Article.ArticleStatus.DRAFT).count()
        context['pending_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.PENDING_ADMIN
        ).count()
        context['in_review_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.IN_REVIEW
        ).count()
        context['changes_requested'] = Article.objects.filter(
            status=Article.ArticleStatus.CHANGES_REQUESTED
        ).count()
        context['rejected_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.REJECTED
        ).count()
        context['published_articles'] = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).count()
        
        # User statistics
        context['total_reviewers'] = User.objects.filter(
            role=CustomUser.UserRole.REVIEWER
        ).count()
        context['active_reviewers'] = User.objects.filter(
            role=CustomUser.UserRole.REVIEWER,
            is_active=True
        ).count()
        context['total_authors'] = User.objects.filter(
            role=CustomUser.UserRole.AUTHOR
        ).count()
        
        # Journal statistics
        context['total_journals'] = Journal.objects.count()
        context['active_journals'] = Journal.objects.filter(is_active=True).count()
        
        # Recent pending articles
        context['recent_pending'] = Article.objects.filter(
            status=Article.ArticleStatus.PENDING_ADMIN
        ).select_related('author').order_by('-submitted_at')[:5]
        
        # Top reviewers by reviews count
        context['top_reviewers'] = User.objects.filter(
            role=CustomUser.UserRole.REVIEWER
        ).annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:5]
        
        return context


class ReviewerListView(AdminAccessMixin, ListView):
    """List all reviewers."""
    model = User
    template_name = 'admin_panel/reviewer_list.html'
    context_object_name = 'reviewers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.filter(
            role=CustomUser.UserRole.REVIEWER
        ).annotate(
            review_count=Count('reviews')
        ).order_by('-created_at')
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ReviewerCreateView(AdminAccessMixin, CreateView):
    """Create a new reviewer."""
    model = User
    form_class = ReviewerCreationForm
    template_name = 'admin_panel/reviewer_form.html'
    success_url = reverse_lazy('admin_panel:reviewer_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Reviewer created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create New Reviewer')
        return context


class ReviewerDetailView(AdminAccessMixin, DetailView):
    """View reviewer details and their assignments."""
    model = User
    template_name = 'admin_panel/reviewer_detail.html'
    context_object_name = 'reviewer'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        return User.objects.filter(role=CustomUser.UserRole.REVIEWER)
    
    def get_context_data(self, **kwargs):
        from articles.models import ReviewerAssignment
        
        context = super().get_context_data(**kwargs)
        reviewer = self.object
        
        # Get all assignments for this reviewer
        all_assignments = ReviewerAssignment.objects.filter(
            reviewer=reviewer
        ).select_related('article', 'article__author').order_by('-assigned_at')
        
        context['all_assignments'] = all_assignments
        context['recent_assignments'] = all_assignments[:10]
        
        # Statistics
        context['total_assignments'] = all_assignments.count()
        context['approved_count'] = all_assignments.filter(
            status=ReviewerAssignment.AssignmentStatus.APPROVED
        ).count()
        context['rejected_count'] = all_assignments.filter(
            status=ReviewerAssignment.AssignmentStatus.REJECTED
        ).count()
        context['changes_count'] = all_assignments.filter(
            status=ReviewerAssignment.AssignmentStatus.CHANGES_REQUESTED
        ).count()
        context['pending_count'] = all_assignments.filter(
            status=ReviewerAssignment.AssignmentStatus.PENDING
        ).count()
        
        # Group journals from article publication info
        journals_dict = {}
        for assignment in all_assignments:
            article = assignment.article
            if article.publication_year and article.publication_number:
                key = (article.publication_year, article.publication_number)
                if key not in journals_dict:
                    journals_dict[key] = {'year': article.publication_year, 'number': article.publication_number, 'count': 0}
                journals_dict[key]['count'] += 1
        
        context['journals'] = list(journals_dict.values())
        
        return context


class ReviewerEditView(AdminAccessMixin, UpdateView):
    """Edit reviewer details and assignments."""
    model = User
    form_class = ReviewerEditForm
    template_name = 'admin_panel/reviewer_form.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        return User.objects.filter(role=CustomUser.UserRole.REVIEWER)
    
    def form_valid(self, form):
        messages.success(self.request, _('Reviewer updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit Reviewer')
        return context
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:reviewer_detail', kwargs={'pk': self.object.pk})


class ReviewerDeleteView(AdminAccessMixin, DeleteView):
    """Delete a reviewer."""
    model = User
    template_name = 'admin_panel/reviewer_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:reviewer_list')
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        return User.objects.filter(role=CustomUser.UserRole.REVIEWER)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Reviewer deleted successfully.'))
        return super().delete(request, *args, **kwargs)


class ArticleManageView(AdminAccessMixin, ListView):
    """Manage all articles with status filtering."""
    model = Article
    template_name = 'admin_panel/article_manage.html'
    context_object_name = 'articles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Article.objects.select_related('author').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status and status in dict(Article.ArticleStatus.choices):
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title_uz__icontains=search) |
                Q(title_ru__icontains=search) |
                Q(title_en__icontains=search) |
                Q(author__username__icontains=search) |
                Q(author__email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Article.ArticleStatus.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        context['pending_count'] = Article.objects.filter(
            status=Article.ArticleStatus.PENDING_ADMIN
        ).count()
        return context


class ArticleActionView(AdminAccessMixin, DetailView, FormView):
    """Take action on an article (publish, reject, request changes)."""
    model = Article
    form_class = ArticleActionForm
    assignment_form_class = ReviewerAssignmentForm
    template_name = 'admin_panel/article_action.html'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context['article'] = article
        context['reviews'] = Review.objects.filter(article=article).select_related('reviewer')
        context['assignments'] = ReviewerAssignment.objects.filter(
            article=article
        ).select_related('reviewer', 'assigned_by').order_by('-assigned_at')
        assignment_form = kwargs.get('assignment_form')
        context['assignment_form'] = assignment_form or self.assignment_form_class()
        return context
    
    def post(self, request, *args, **kwargs):
        if 'assign_reviewers' in request.POST:
            assignment_form = self.assignment_form_class(request.POST)
            if assignment_form.is_valid():
                return self.form_valid_assignment(assignment_form)
            return self.render_to_response(self.get_context_data(
                form=self.form_class(),
                assignment_form=assignment_form
            ))

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def form_valid_assignment(self, form):
        article = self.get_object()
        reviewers = form.cleaned_data['reviewers']
        success, message, count = ArticleWorkflow.assign_reviewers(
            article,
            reviewers,
            self.request.user
        )

        if success:
            if count:
                messages.success(self.request, message)
            else:
                messages.info(self.request, _('Selected reviewers are already assigned.'))
        else:
            messages.error(self.request, message)

        return redirect(self.request.path)

    def form_valid(self, form):
        article = self.get_object()
        action = form.cleaned_data['action']
        note = form.cleaned_data.get('note', '')
        publication_year = form.cleaned_data.get('publication_year')
        publication_number = form.cleaned_data.get('publication_number')

        # Set publication information before workflow actions
        updated_pub = False
        if publication_year:
            article.publication_year = publication_year
            updated_pub = True
        if publication_number:
            article.publication_number = publication_number
            updated_pub = True
        if updated_pub:
            article.save(update_fields=['publication_year', 'publication_number', 'updated_at'])

        # Use workflow methods for proper notifications and logging
        if action == 'publish':
            success, message = ArticleWorkflow.publish_article(article, self.request.user, note)
            if success:
                messages.success(self.request, _('Article published successfully.'))
            else:
                messages.error(self.request, message)

        elif action == 'reject':
            success, message = ArticleWorkflow.reject_article(article, self.request.user, note)
            if success:
                messages.success(self.request, _('Article rejected.'))
            else:
                messages.error(self.request, message)

        elif action == 'request_changes':
            success, message = ArticleWorkflow.request_changes_from_author(article, self.request.user, note)
            if success:
                messages.success(self.request, _('Change request sent to author.'))
            else:
                messages.error(self.request, message)

        elif action == 'reset_status':
            article.status = Article.ArticleStatus.IN_REVIEW
            article.admin_decision_by = self.request.user
            article.admin_decision_at = timezone.now()
            article.save()
            messages.success(self.request, _('Article status reset to In Review.'))

        return redirect('admin_panel:article_manage')


class BulkArticleActionView(AdminAccessMixin, FormView):
    """Perform bulk actions on articles."""
    form_class = BulkArticleActionForm
    template_name = 'admin_panel/bulk_article_action.html'
    success_url = reverse_lazy('admin_panel:article_manage')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article_ids = self.request.GET.getlist('articles')
        context['articles'] = Article.objects.filter(id__in=article_ids)
        context['article_ids'] = article_ids
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        action = form.cleaned_data['action']
        note = form.cleaned_data.get('note', '')
        article_ids = self.request.POST.getlist('article_ids')
        articles = Article.objects.filter(id__in=article_ids)
        
        count = 0
        for article in articles:
            if action == 'publish':
                article.status = Article.ArticleStatus.PUBLISHED
                article.published_at = timezone.now()
            elif action == 'reject':
                article.status = Article.ArticleStatus.REJECTED
                article.admin_note = note
            elif action == 'request_changes':
                article.status = Article.ArticleStatus.CHANGES_REQUESTED
                article.admin_note = note
            
            article.admin_decision_by = self.request.user
            article.admin_decision_at = timezone.now()
            article.save()
            count += 1
        
        messages.success(self.request, _('Action performed on {} articles.'.format(count)))
        return redirect(self.get_success_url())


class SystemStatsView(AdminAccessMixin, TemplateView):
    """Display system-wide statistics and analytics."""
    template_name = 'admin_panel/system_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Article statistics
        context['article_stats'] = {
            'total': Article.objects.count(),
            'by_status': dict(
                Article.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'total_views': Article.objects.aggregate(Count('views'))['views__count'] or 0,
        }
        
        # User statistics
        context['user_stats'] = {
            'total_users': User.objects.count(),
            'by_role': dict(
                User.objects.values('role').annotate(count=Count('id')).values_list('role', 'count')
            ),
            'active_users': User.objects.filter(is_active=True).count(),
        }
        
        # Review statistics
        context['review_stats'] = {
            'total_reviews': Review.objects.count(),
            'by_decision': dict(
                Review.objects.values('decision').annotate(count=Count('id')).values_list('decision', 'count')
            ),
            'average_reviews_per_article': Review.objects.values('article').annotate(count=Count('id')).aggregate(avg=Count('id') / (Article.objects.filter(status=Article.ArticleStatus.PUBLISHED).count() or 1))['avg'],
        }
        
        return context


class JournalListView(AdminAccessMixin, ListView):
    model = Journal
    template_name = 'admin_panel/journal_list.html'
    context_object_name = 'journals'
    paginate_by = 20
    def get_queryset(self):
        return Journal.objects.order_by('-year', '-number')

class JournalCreateView(AdminAccessMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'admin_panel/journal_form.html'
    success_url = reverse_lazy('admin_panel:journal_list')
    def form_valid(self, form):
        messages.success(self.request, _('Journal created successfully.'))
        return super().form_valid(form)

class JournalUpdateView(AdminAccessMixin, UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = 'admin_panel/journal_form.html'
    success_url = reverse_lazy('admin_panel:journal_list')
    def form_valid(self, form):
        messages.success(self.request, _('Journal updated successfully.'))
        return super().form_valid(form)

class JournalDeactivateView(AdminAccessMixin, UpdateView):
    model = Journal
    fields = ['is_active']
    template_name = 'admin_panel/journal_confirm_deactivate.html'
    success_url = reverse_lazy('admin_panel:journal_list')
    def form_valid(self, form):
        form.instance.is_active = False
        messages.success(self.request, _('Journal deactivated.'))
        return super().form_valid(form)
