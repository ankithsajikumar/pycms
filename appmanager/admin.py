from django.contrib import admin
from .models import App

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    fields = ('user', 'name', 'repo_url', 'subdomain', 'status', 'build_file')