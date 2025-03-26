from django.contrib import admin
from .models import PolicyCategory, Policy

@admin.register(PolicyCategory)
class PolicyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'title', 'category', 'status', 'effective_date', 'review_date')
    list_filter = ('status', 'category', 'effective_date')
    search_fields = ('title', 'policy_number', 'content', 'summary')
    date_hierarchy = 'effective_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'policy_number', 'category')
        }),
        ('Content', {
            'fields': ('content', 'summary', 'document_file')
        }),
        ('Status and Dates', {
            'fields': ('status', 'effective_date', 'review_date')
        }),
        ('Ownership', {
            'fields': ('created_by', 'updated_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
