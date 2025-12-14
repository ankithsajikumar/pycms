from django.shortcuts import render
from django.http import Http404
from django.template.exceptions import TemplateDoesNotExist
from .models import App

def serve_static_app(request, app_name, subpath=None):
    """
    Serve the React app's versioned index.html for the given app_name.
    If the template does not exist, return a 404 response.
    """
    try:
        app = App.objects.get(name=app_name)
        if not app.buildnumber:
            raise Http404(f"No build deployed for '{app_name}'.")
        template_name = f'apps/{app_name}/index_{app.buildnumber}.html'
        return render(request, template_name)
    except (App.DoesNotExist, TemplateDoesNotExist):
        raise Http404(f"The app '{app_name}' does not have a valid index.html template.")