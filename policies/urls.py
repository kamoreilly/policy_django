from django.urls import path
from . import views

app_name = 'policies'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('policies/', views.PolicyListView.as_view(), name='policy-list'),
    path('policies/<int:pk>/', views.PolicyDetailView.as_view(), name='policy-detail'),
    path('policies/create/', views.PolicyCreateView.as_view(), name='policy-create'),
    path('policies/<int:pk>/update/', views.PolicyUpdateView.as_view(), name='policy-update'),
    path('policies/<int:pk>/delete/', views.PolicyDeleteView.as_view(), name='policy-delete'),
    path('categories/', views.PolicyCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.PolicyCategoryDetailView.as_view(), name='category-detail'),
    path('categories/create/', views.PolicyCategoryCreateView.as_view(), name='category-create'),
    
    # HTMX endpoints
    path('htmx/policy-list/', views.policy_htmx_list, name='htmx-policy-list'),
]