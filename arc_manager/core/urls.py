from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.http import JsonResponse

def root_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return redirect('main:dashboard')

def health_check(request):
    """Endpoint for AWS Beanstalk health check"""
    return JsonResponse({'status': 'healthy', 'service': 'arc-manager'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('main/', include('apps.main.urls')),
    path('organizations/', include('apps.orgs.urls')),
    path('users/', include('apps.users.urls')),
    path('plans/', include('apps.plans.urls')),
    path('projects/', include('apps.projects.urls')),
    path('health/', health_check, name='health_check'),
    path('', root_redirect),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers for production
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'
