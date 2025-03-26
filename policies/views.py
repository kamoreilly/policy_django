from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string
# Temporarily comment out WeasyPrint imports
# from weasyprint import HTML, CSS
from django.conf import settings
import tempfile
import os

from .models import Policy, PolicyCategory
from .forms import PolicyForm, PolicyCategoryForm, PolicySearchForm

class HomeView(ListView):
    """Home page view showing published policies."""
    model = Policy
    template_name = 'policies/home.html'
    context_object_name = 'policies'
    paginate_by = 10
    
    def get_queryset(self):
        """Return only published policies for regular users."""
        queryset = Policy.objects.filter(status='published')
        
        # If the user is staff, show all policies
        if self.request.user.is_authenticated and (
            self.request.user.profile.is_admin or 
            self.request.user.profile.is_moderator
        ):
            queryset = Policy.objects.all()
            
        # Handle search form
        form = PolicySearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            status = form.cleaned_data.get('status')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(policy_number__icontains=query) |
                    Q(content__icontains=query) |
                    Q(summary__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
                
            if status:
                queryset = queryset.filter(status=status)
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PolicySearchForm(self.request.GET or None)
        context['categories'] = PolicyCategory.objects.all()
        return context

class PolicyDetailView(DetailView):
    """View for displaying a single policy."""
    model = Policy
    template_name = 'policies/policy_detail.html'
    context_object_name = 'policy'
    
    def get_queryset(self):
        """Only show published policies to regular users."""
        if self.request.user.is_authenticated and (
            self.request.user.profile.is_admin or 
            self.request.user.profile.is_moderator
        ):
            return Policy.objects.all()
        return Policy.objects.filter(status='published')

class ManagementRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin or moderator permissions."""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.profile.is_admin or
            self.request.user.profile.is_moderator
        )

class PolicyCategoryListView(LoginRequiredMixin, ManagementRequiredMixin, ListView):
    """View for listing all policy categories."""
    model = PolicyCategory
    template_name = 'policies/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

class PolicyCategoryDetailView(DetailView):
    """View for displaying policies by category."""
    model = PolicyCategory
    template_name = 'policies/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        policies = Policy.objects.filter(category=self.object)
        
        if not self.request.user.is_authenticated or not (self.request.user.profile.is_admin or self.request.user.profile.is_moderator):
            policies = policies.filter(status='published')
        
        context['policies'] = policies
        return context
    """Mixin to require admin or moderator permissions."""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.profile.is_admin or 
            self.request.user.profile.is_moderator
        )

# HTMX-enhanced views for policy management

class PolicyCreateView(LoginRequiredMixin, ManagementRequiredMixin, CreateView):
    """View for creating new policies."""
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policy-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Policy created successfully.')
        return super().form_valid(form)

class PolicyUpdateView(LoginRequiredMixin, ManagementRequiredMixin, UpdateView):
    """View for updating policies."""
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'
    success_url = reverse_lazy('policies:policy-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Policy updated successfully.')
        return super().form_valid(form)

class PolicyDeleteView(LoginRequiredMixin, ManagementRequiredMixin, DeleteView):
    """View for deleting policies."""
    model = Policy
    template_name = 'policies/policy_confirm_delete.html'
    success_url = reverse_lazy('policy-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Policy deleted successfully.')
        return super().delete(request, *args, **kwargs)

class PolicyListView(LoginRequiredMixin, ListView):
    """View for listing all policies with management options."""
    model = Policy
    template_name = 'policies/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20
    
    def get_queryset(self):
        """Return all policies for admins/moderators, only published for users."""
        if self.request.user.profile.is_admin or self.request.user.profile.is_moderator:
            return Policy.objects.all()
        return Policy.objects.filter(status='published')

class PolicyCategoryCreateView(LoginRequiredMixin, ManagementRequiredMixin, CreateView):
    """View for creating new policy categories."""
    model = PolicyCategory
    form_class = PolicyCategoryForm
    template_name = 'policies/category_form.html'
    success_url = reverse_lazy('admin-dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)

# HTMX partial views for dynamic content loading
@login_required
def policy_htmx_list(request):
    """HTMX-powered view for dynamically loading policy lists."""
    search_form = PolicySearchForm(request.GET)
    policies = Policy.objects.all()
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        status = search_form.cleaned_data.get('status')
        
        if query:
            policies = policies.filter(
                Q(title__icontains=query) | 
                Q(policy_number__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query)
            )
        
        if category:
            policies = policies.filter(category=category)
            
        if status:
            policies = policies.filter(status=status)
    
    # Filter by permissions
    if not (request.user.profile.is_admin or request.user.profile.is_moderator):
        policies = policies.filter(status='published')
            
    return render(request, 'policies/partials/policy_list.html', {
        'policies': policies
    })
