"""pycms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include
from django_sso_client_oauth import views as sso_views
from django.http import HttpResponseRedirect
from django.conf.urls.static import static
from appmanager.views import serve_static_app
from rest_framework.routers import DefaultRouter
from appmanager.views import AppViewSet

def home_redirect(request):
    return HttpResponseRedirect(settings.HOME_URL)

router = DefaultRouter()
router.register(r'apps', AppViewSet, basename='app')

urlpatterns = [
    path('', home_redirect),
    path("admin/login/", sso_views.login, name="login"),
    path("auth/callback/", sso_views.callback, name="callback"),
    path('admin/', admin.site.urls),
    re_path(
        r'^apps/(?P<app_name>[^/]+)/(?P<subpath>.+?)/?$',
        serve_static_app,
        name='serve_static_app'
    ),

    re_path(
        r'^apps/(?P<app_name>[^/]+)/?$',
        serve_static_app,
        name='serve_static_app_root'
    ),
    path('api/', include(router.urls)),
]

admin.site.site_header = 'CMS Administration'
admin.site.index_title = 'Content Management'
admin.site.site_title = 'Hacksaw CMS'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
