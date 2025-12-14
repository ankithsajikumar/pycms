from django.shortcuts import render
from django.http import Http404
from django.template.exceptions import TemplateDoesNotExist
from .models import App

def serve_static_app(request, app_name, subpath=None):
    """
    Serve the React app's versioned index.html for the given app_name.
    If the versioned template does not exist or no buildnumber, fall back to index.html.
    If neither exists, return a 404 response.
    """
    try:
        app = App.objects.get(name=app_name)
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