import os
import zipfile
import time
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import App

@receiver(pre_save, sender=App)
def remove_old_zip_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, nothing to do
    try:
        old_instance = App.objects.get(pk=instance.pk)
    except App.DoesNotExist:
        return
    old_file = old_instance.build_file
    new_file = instance.build_file
    if old_file and old_file != new_file and os.path.exists(old_file.path):
        try:
            os.remove(old_file.path)
        except Exception:
            pass
    # Remove old template if buildnumber will change
    if old_instance.buildnumber and old_instance.buildnumber != instance.buildnumber:
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
        old_template = os.path.join(templates_dir, f'index_{old_instance.buildnumber}.html')
        if os.path.exists(old_template):
            try:
                os.remove(old_template)
            except Exception:
                pass

@receiver(post_save, sender=App)
def handle_build_artifact(sender, instance, created, **kwargs):
    if instance.build_file:
        # Set buildnumber to current timestamp
        buildnumber = int(time.time())
        App.objects.filter(pk=instance.pk).update(buildnumber=buildnumber)
        instance.buildnumber = buildnumber  # update in-memory instance

        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
        static_dir = os.path.join(settings.STATIC_PATH_INSTALLED_APPS, instance.name)
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        build_path = instance.build_file.path
        with zipfile.ZipFile(build_path, 'r') as zip_ref:
            zip_ref.extractall(static_dir)
        index_html_path = os.path.join(static_dir, 'index.html')
        template_target = os.path.join(templates_dir, f'index_{buildnumber}.html')
        if os.path.exists(index_html_path):
            os.rename(index_html_path, template_target)

@receiver(post_delete, sender=App)
def remove_build_artifact(sender, instance, **kwargs):
    templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', instance.name)
    static_dir = os.path.join(settings.STATIC_PATH_INSTALLED_APPS, instance.name)
    # Remove the versioned template
    if instance.buildnumber:
        template_path = os.path.join(templates_dir, f'index_{instance.buildnumber}.html')
        if os.path.exists(template_path):
            try:
                os.remove(template_path)
            except Exception:
                pass
    # Remove the templates directory if empty
    if os.path.exists(templates_dir) and not os.listdir(templates_dir):
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
    # Remove the uploaded zip file if it exists
    if instance.build_file and os.path.exists(instance.build_file.path):
        try:
            os.remove(instance.build_file.path)
        except Exception:
            pass
