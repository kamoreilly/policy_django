from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
