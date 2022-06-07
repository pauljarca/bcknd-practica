"""practica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import private_storage.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from graphene_django.views import GraphQLView

from internships.views import ExportApplicantsView
from students.views import StudentCVDownloadView, StudentCVUploadView


if getattr(settings, 'REVPROXY_FRONTEND_URL', ''):
    # noinspection PyUnresolvedReferences
    from drfreverseproxy.views import ProxyView
    proxy_view = ProxyView.as_view(upstream=settings.REVPROXY_FRONTEND_URL)

    # noinspection PyUnusedLocal
    def dummy_view(request, *args, **kwargs):
        return proxy_view(request, request.path)
else:
    # noinspection PyUnusedLocal
    def dummy_view(request, *args, **kwargs):
        raise NotImplementedError("This view should be routed to client-side code.")


urlpatterns = [
    path('admin/ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('admin', RedirectView.as_view(url='/admin/')),
    path('accounts/', include('allauth.urls')),

    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('graphql/', RedirectView.as_view(url='/graphql')),

    path('private/cv/<uuid:pk>/<str:basename>', StudentCVDownloadView.as_view(), name='download_student_cv'),
    path('private/applicants/export/<uuid:pk>', ExportApplicantsView.as_view(), name='export_company_applicants'),
    path('private/', include(private_storage.urls)),

    path('upload/cv', csrf_exempt(StudentCVUploadView.as_view())),

    # client-side route mappings for use with reverse()
    path('user/confirm-email/<str:key>', dummy_view, name='account_confirm_email'),
    path('user/reset-password/<str:uidb36>/<str:key>', dummy_view, name='account_reset_password_from_key'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if getattr(settings, 'REVPROXY_FRONTEND_URL', ''):
    # noinspection PyUnresolvedReferences
    from drfreverseproxy.views import ProxyView

    urlpatterns += re_path(r'^(?P<path>.*)$', ProxyView.as_view(upstream=settings.REVPROXY_FRONTEND_URL)),
