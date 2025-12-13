from django.shortcuts import render
from django.http import Http404
from django.template.exceptions import TemplateDoesNotExist

def serve_static_app(request, app_name, subpath=None):
    """
    Serve the React app's index.html for the given app_name.
    If the template does not exist, return a 404 response.
    """
    try:
        return render(request, f'apps/{app_name}/index.html')
    except TemplateDoesNotExist:
        raise Http404(f"The app '{app_name}' does not have an index.html template.")