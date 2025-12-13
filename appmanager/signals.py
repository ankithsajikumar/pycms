import os
import zipfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import App

@receiver(post_save, sender=App)
def handle_build_artifact(sender, instance, created, **kwargs):
    if created and instance.build_file:
        # Define paths for templates and static
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
        static_dir = os.path.join(settings.STATIC_PATH_INSTALLED_APPS, instance.name)

        # Create directories if they don't exist
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)

        # Extract the uploaded .zip file
        build_path = instance.build_file.path
        with zipfile.ZipFile(build_path, 'r') as zip_ref:
            zip_ref.extractall(static_dir)

        # Move the `index.html` file to the templates directory
        index_html_path = os.path.join(static_dir, 'index.html')
        if os.path.exists(index_html_path):
            os.rename(index_html_path, os.path.join(templates_dir, 'index.html'))