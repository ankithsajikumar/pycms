import os
import mimetypes
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views.decorators.common import no_append_slash
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import App
from .serializers import AppSerializer
import shutil

ASSET_EXTENSIONS = {'.json', '.ico', '.png', '.jpg', '.jpeg', '.svg', '.webmanifest', '.txt', '.js', '.css'}

@no_append_slash
def serve_static_app(request, app_name, subpath=None):
    """
    Serve the React app's index.html or static assets like manifest.json, favicon, etc.
    """
    try:
        app = App.objects.get(name=app_name)
        templates_dir = os.path.join(settings.TEMPLATES_DIR, app_name)
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
            template_names.append(f'{app_name}/index_{app.buildnumber}.html')
        template_names.append(f'{app_name}/index.html')
        for template_name in template_names:
            try:
                return render(request, template_name)
            except TemplateDoesNotExist:
                continue
        raise Http404(f"The app '{app_name}' does not have a valid index.html template.")
    except App.DoesNotExist:
        raise Http404(f"The app '{app_name}' does not exist.")

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        # Filter apps by current user
        return App.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Auto-set the user to the current user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def deploy(self, request, pk=None):
        """
        Deploy a new version of the app by uploading:
        1. A single build file (.zip or .tar.gz)
        2. Multiple files (which will be extracted to the app directory)
        
        Endpoint: POST /api/apps/{id}/deploy/
        """
        app = self.get_object()
        
        # Check for compressed file first
        if 'build_file' in request.FILES:
            build_file = request.FILES['build_file']
            app.build_file = build_file
            app.save()
            return Response(
                {
                    'message': f"App '{app.name}' deployed successfully",
                    'app': AppSerializer(app).data
                },
                status=status.HTTP_200_OK
            )
        
        # Check for multiple files (directory upload)
        files = request.FILES.getlist('files')
        if files:
            return self._deploy_from_files(app, files)
        
        return Response(
            {'error': 'Either build_file or files are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _deploy_from_files(self, app, files):
        """
        Deploy app from multiple uploaded files.
        Reconstructs the directory structure in the templates directory.
        """
        try:
            templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'apps', app.name)
            os.makedirs(templates_dir, exist_ok=True)
            
            # Save all files to the templates directory, preserving relative paths
            for file in files:
                file_path = os.path.join(templates_dir, file.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
            
            # Create versioned index.html
            index_html_path = os.path.join(templates_dir, 'index.html')
            if os.path.exists(index_html_path):
                import time
                buildnumber = int(time.time())
                App.objects.filter(pk=app.pk).update(buildnumber=buildnumber)
                versioned_template = os.path.join(templates_dir, f'index_{buildnumber}.html')
                shutil.copy2(index_html_path, versioned_template)
            
            return Response(
                {
                    'message': f"App '{app.name}' deployed successfully from files",
                    'app': AppSerializer(app).data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to deploy: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def undeploy(self, request, pk=None):
        """
        Remove the app and all its artifacts.
        Endpoint: POST /api/apps/{id}/undeploy/
        """
        app = self.get_object()
        app_name = app.name
        app.delete()
        return Response(
            {'message': f"App '{app_name}' undeployed successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def restart(self, request, pk=None):
        """
        Restart/redeploy the app (keep the same build).
        Endpoint: POST /api/apps/{id}/restart/
        """
        app = self.get_object()
        if not app.build_file:
            return Response(
                {'error': 'No build file to restart'},
                status=status.HTTP_400_BAD_REQUEST
            )
        app.save()  # Triggers the post_save signal
        return Response(
            {
                'message': f"App '{app.name}' restarted successfully",
                'app': AppSerializer(app).data
            },
            status=status.HTTP_200_OK
        )