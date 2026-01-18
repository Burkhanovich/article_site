"""
Views for user authentication and management.
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserRegistrationForm, CustomLoginForm, ArticleRulesAcceptanceForm
from .models import ArticleRules


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
    User dashboard - different views for authors and readers.
    """
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        """Add user-specific data to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_author:
            # Import here to avoid circular import
            from articles.models import Article

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

        return context
