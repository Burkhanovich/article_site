"""
Views for user authentication and management.
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView

from .forms import CustomUserRegistrationForm, CustomLoginForm, ArticleRulesAcceptanceForm
from .models import ArticleRules, Notification


class UserRegistrationView(CreateView):
    """
    Handle user registration with role selection.
    Redirect authors to rules page after registration.
    """
    model = None
    form_class = CustomUserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users."""
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Save user and redirect based on role."""
        user = form.save()

        # Log the user in
        login(self.request, user)

        # Success message
        messages.success(
            self.request,
            f'Welcome, {user.username}! Your account has been created successfully.'
        )

        # Redirect authors to rules acceptance page
        if user.is_author:
            messages.info(
                self.request,
                'As an author, you must read and accept our article writing rules before publishing.'
            )
            return redirect('users:accept_rules')

        # Redirect readers to home
        return redirect('core:home')

    def form_invalid(self, form):
        """Display error messages."""
        messages.error(
            self.request,
            'Registration failed. Please correct the errors below.'
        )
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """
    Custom login view with role-based redirection.
    """
    form_class = CustomLoginForm
    template_name = 'users/login.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users."""
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Redirect based on user role and rules acceptance."""
        user = self.request.user

        # Check if author hasn't accepted rules
        if user.is_author and not user.has_accepted_rules:
            messages.info(
                self.request,
                'Please accept the article writing rules to start publishing.'
            )
            return reverse_lazy('users:accept_rules')

        # Default redirect
        return reverse_lazy('core:dashboard')

    def form_valid(self, form):
        """Display success message on login."""
        messages.success(
            self.request,
            f'Welcome back, {form.get_user().username}!'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Display error message on failed login."""
        messages.error(
            self.request,
            'Invalid username or password. Please try again.'
        )
        return super().form_invalid(form)


class CustomLogoutView(View):
    """
    Handle user logout.
    """

    def get(self, request):
        """Log out user and redirect."""
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('core:home')


class ArticleRulesAcceptanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Display article rules to authors and handle acceptance.
    Only accessible by authors who haven't accepted rules.
    """
    template_name = 'users/accept_rules.html'

    def test_func(self):
        """Only authors can access this page."""
        return self.request.user.is_author

    def handle_no_permission(self):
        """Redirect non-authors with error message."""
        messages.error(
            self.request,
            'Access denied. This page is only for authors.'
        )
        return redirect('core:home')

    def get_context_data(self, **kwargs):
        """Add rules and form to context."""
        context = super().get_context_data(**kwargs)
        context['rules'] = ArticleRules.get_active_rules()
        context['form'] = ArticleRulesAcceptanceForm()

        # Show warning if no rules exist
        if not context['rules']:
            messages.warning(
                self.request,
                'Article rules have not been configured yet. Please contact the administrator.'
            )

        return context

    def post(self, request, *args, **kwargs):
        """Handle rules acceptance."""
        form = ArticleRulesAcceptanceForm(request.POST)

        if form.is_valid():
            # Mark user as having accepted rules
            user = request.user
            user.has_accepted_rules = True
            user.save()

            messages.success(
                request,
                'Thank you for accepting the rules! You can now create articles.'
            )
            return redirect('core:dashboard')

        # Form invalid
        messages.error(
            request,
            'You must accept the rules to proceed.'
        )
        return self.get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User dashboard - different views for authors, reviewers, and readers.
    """
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        """Add user-specific data to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Import here to avoid circular import
        from articles.models import Article, Review
        from .models import Notification

        # Get notifications for all users
        context['unread_notifications'] = Notification.objects.filter(
            user=user, is_read=False
        ).count()
        context['recent_notifications'] = Notification.objects.filter(
            user=user
        )[:5]

        if user.is_author or user.can_create_articles:
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
            context['pending_articles'] = Article.objects.filter(
                author=user,
                status__in=[
                    Article.ArticleStatus.PENDING_ADMIN,
                    Article.ArticleStatus.IN_REVIEW
                ]
            ).count()
            context['changes_requested_articles'] = Article.objects.filter(
                author=user,
                status=Article.ArticleStatus.CHANGES_REQUESTED
            ).count()
            context['rejected_articles'] = Article.objects.filter(
                author=user,
                status=Article.ArticleStatus.REJECTED
            ).count()

            # Recent articles
            context['recent_articles'] = Article.objects.filter(
                author=user
            ).select_related('author').prefetch_related('categories').order_by('-created_at')[:5]

            # Recent reviews received on user's articles
            context['recent_reviews_received'] = Review.objects.filter(
                article__author=user
            ).select_related('reviewer', 'category', 'article').order_by('-created_at')[:5]

        if user.is_reviewer or user.can_review_articles:
            # Reviewer statistics
            from articles.services import get_reviewer_queue

            context['reviewer_queue'] = get_reviewer_queue(user)
            context['my_reviews'] = Review.objects.filter(
                reviewer=user
            ).select_related('article', 'category').order_by('-created_at')[:10]
            context['total_reviews'] = Review.objects.filter(reviewer=user).count()

        return context


class NotificationListView(LoginRequiredMixin, ListView):
    """
    List all notifications for the current user.
    """
    model = Notification
    template_name = 'users/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        """Get notifications for the current user."""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).count()
        return context


class MarkNotificationReadView(LoginRequiredMixin, View):
    """
    Mark a single notification as read.
    """

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user
        )
        notification.mark_as_read()

        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        # Otherwise redirect to the notification link or back
        if notification.link:
            return redirect(notification.link)
        return redirect('users:notifications')


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """
    Mark all notifications as read for the current user.
    """

    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        messages.success(request, _('All notifications marked as read.'))

        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        return redirect('users:notifications')
