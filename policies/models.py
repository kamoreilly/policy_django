from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os

class PolicyCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Policy Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])


def policy_file_path(instance, filename):
    # Generate file path for policy documents
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('policies', filename)


class Policy(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(PolicyCategory, on_delete=models.CASCADE, related_name='policies')
    content = models.TextField()
    summary = models.TextField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_policies')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_policies')
    
    effective_date = models.DateField()
    review_date = models.DateField()
    
    document_file = models.FileField(upload_to=policy_file_path, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Policies"
        ordering = ['-effective_date', 'title']
        
    def __str__(self):
        return f"{self.policy_number} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('policy-detail', args=[str(self.id)])
    
    @property
    def is_published(self):
        return self.status == 'published'
        
    @property
    def needs_review(self):
        return self.review_date <= timezone.now().date()
