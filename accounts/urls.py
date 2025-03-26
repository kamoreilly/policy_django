from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('moderator-dashboard/', views.ModeratorDashboardView.as_view(), name='moderator-dashboard'),
    path('user/<int:pk>/edit/', views.UserEditView.as_view(), name='user-edit'),
    path('user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # User approval URLs
    path('user-approval/', views.UserApprovalView.as_view(), name='user-approval'),
    path('user/<int:pk>/approve/', views.approve_user, name='approve-user'),
    path('user/<int:pk>/reject/', views.reject_user, name='reject-user'),
]