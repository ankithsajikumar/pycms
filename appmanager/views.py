from django.shortcuts import render

def serve_static_app(request, app_name, subpath):
    return render(request, f'apps/{app_name}/index.html')