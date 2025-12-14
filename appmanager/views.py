import os
import mimetypes
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views.decorators.common import no_append_slash
from .models import App

ASSET_EXTENSIONS = {'.json', '.ico', '.png', '.jpg', '.jpeg', '.svg', '.webmanifest', '.txt', '.js', '.css'}

@no_append_slash
def serve_static_app(request, app_name, subpath=None):
    """
    Serve the React app's index.html or static assets like manifest.json, favicon, etc.
    """
    try:
        app = App.objects.get(name=app_name)
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', app_name)
        # If subpath is an asset, serve it directly from the templates directory
        if subpath:
            ext = os.path.splitext(subpath)[1].lower()
            if ext and ext in ASSET_EXTENSIONS:
                asset_path = os.path.join(templates_dir, subpath)
                if os.path.isfile(asset_path):
                    content_type, _ = mimetypes.guess_type(asset_path)
                    return FileResponse(open(asset_path, 'rb'), content_type=content_type)
                else:
                    raise Http404(f"Asset '{subpath}' not found for app '{app_name}'.")
        # Otherwise, serve the React app's index.html (versioned or fallback)
        template_names = []
        if app.buildnumber:
            template_names.append(f'apps/{app_name}/index_{app.buildnumber}.html')
        template_names.append(f'apps/{app_name}/index.html')
        for template_name in template_names:
            try:
                return render(request, template_name)
            except TemplateDoesNotExist:
                continue
        raise Http404(f"The app '{app_name}' does not have a valid index.html template.")
    except App.DoesNotExist:
        raise Http404(f"The app '{app_name}' does not exist.")