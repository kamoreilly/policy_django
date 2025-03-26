from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from .forms import UserRegistrationForm, UserProfileForm, CustomLoginForm, UserEditForm
from .models import UserProfile

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your account has been created and is pending approval. You will be notified once an administrator approves your account.')
        return response

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.profile.is_approved:
            messages.error(self.request, 'Your account is pending approval. Please wait for administrator approval.')
            return self.form_invalid(form)
        # Explicitly set success_url to avoid reverse lookup issues
        self.success_url = reverse_lazy('policies:home')
        return super().form_valid(form)

class CustomLogoutView(auth_views.LogoutView):
    """Custom logout view to add success message."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'You have been successfully logged out.')
        return response

@login_required
def profile_view(request):
    """View for displaying and updating user profile."""
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
    })

class AdminDashboardView(LoginRequiredMixin, ListView):
    """Admin dashboard view for managing users and policies."""
    model = User
    template_name = 'accounts/admin_dashboard.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.all()
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin:
            messages.error(request, 'You do not have permission to access the admin dashboard.')
            return redirect('policies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from policies.models import Policy, PolicyCategory
        from django.utils import timezone
        from django.db.models import Q
        
        # Add policy statistics
        context['total_policies'] = Policy.objects.count()
        context['published_policies'] = Policy.objects.filter(status='published').count()
        context['draft_policies'] = Policy.objects.filter(status='draft').count()
        context['review_needed'] = Policy.objects.filter(review_date__lte=timezone.now().date()).count()
        
        # Add policies and categories for management
        context['policies'] = Policy.objects.all().select_related('category', 'created_by', 'updated_by')
        context['categories'] = PolicyCategory.objects.all()
        
        # Add pending users count
        context['pending_users'] = User.objects.filter(profile__approval_status='pending').count()
        
        # Add search form for policies
        from policies.forms import PolicySearchForm
        context['search_form'] = PolicySearchForm()
        
        return context

class UserApprovalView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for managing user approvals."""
    model = User
    template_name = 'accounts/user_approval.html'
    context_object_name = 'pending_users'
    
    def test_func(self):
        return self.request.user.profile.is_admin
    
    def get_queryset(self):
        return User.objects.filter(profile__approval_status='pending')

@login_required
def approve_user(request, pk):
    """View for approving a user."""
    if not request.user.profile.is_admin:
        messages.error(request, 'You do not have permission to approve users.')
        return redirect('policies:home')
    
    user = get_object_or_404(User, pk=pk)
    user.profile.approval_status = 'approved'
    user.is_active = True
    user.profile.save()
    user.save()
    
    messages.success(request, f'User {user.username} has been approved.')
    return redirect('user-approval')

@login_required
def reject_user(request, pk):
    """View for rejecting a user."""
    if not request.user.profile.is_admin:
        messages.error(request, 'You do not have permission to reject users.')
        return redirect('policies:home')
    
    user = get_object_or_404(User, pk=pk)
    user.profile.approval_status = 'rejected'
    user.is_active = False
    user.profile.save()
    user.save()
    
    messages.success(request, f'User {user.username} has been rejected.')
    return redirect('user-approval')

class ModeratorDashboardView(LoginRequiredMixin, ListView):
    """Moderator dashboard view for managing policies."""
    model = User
    template_name = 'accounts/moderator_dashboard.html'
    context_object_name = 'users'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.profile.is_admin or request.user.profile.is_moderator):
            messages.error(request, 'You do not have permission to access the moderator dashboard.')
            return redirect('policies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from policies.models import Policy
        from django.utils import timezone
        from policies.forms import PolicySearchForm
        
        # Add policy statistics
        context['total_policies'] = Policy.objects.count()
        context['published_policies'] = Policy.objects.filter(status='published').count()
        context['draft_policies'] = Policy.objects.filter(status='draft').count()
        context['review_needed'] = Policy.objects.filter(review_date__lte=timezone.now().date()).count()
        
        # Add policies for management
        context['policies'] = Policy.objects.all().select_related('category')
        
        # Add search form for policies
        context['search_form'] = PolicySearchForm()
        
        return context

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profile.is_admin

class UserEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('admin-dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.username}'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {self.object.username} was updated successfully.')
        return response

class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('admin-dashboard')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f'User {user.username} was deleted successfully.')
        return super().delete(request, *args, **kwargs)
