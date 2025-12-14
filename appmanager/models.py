from django.db import models
from users.models import User
import uuid

class App(models.Model):
    STATUS_CHOICES = [
        ('deploying', 'Deploying'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apps')
    name = models.CharField(max_length=100, unique=True)
    repo_url = models.URLField()
    subdomain = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='deploying')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_deployed = models.DateTimeField(auto_now=True)
    build_file = models.FileField(upload_to='app_builds/', blank=True, null=True)
    buildnumber = models.BigIntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
