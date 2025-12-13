import os
import zipfile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import App

@receiver(post_save, sender=App)
def handle_build_artifact(sender, instance, created, **kwargs):
    if created and instance.build_file:
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
        static_dir = os.path.join(settings.STATIC_PATH_INSTALLED_APPS, instance.name)
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        build_path = instance.build_file.path
        with zipfile.ZipFile(build_path, 'r') as zip_ref:
            zip_ref.extractall(static_dir)
        index_html_path = os.path.join(static_dir, 'index.html')
        if os.path.exists(index_html_path):
            os.rename(index_html_path, os.path.join(templates_dir, 'index.html'))

@receiver(post_delete, sender=App)
def remove_build_artifact(sender, instance, **kwargs):
    templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
    static_dir = os.path.join(settings.STATIC_PATH_INSTALLED_APPS, instance.name)
    if os.path.exists(templates_dir):
        try:
            import shutil
            shutil.rmtree(templates_dir)
        except Exception:
            pass
    if os.path.exists(static_dir):
        try:
            import shutil
            shutil.rmtree(static_dir)
        except Exception:
            pass