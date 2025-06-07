from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static

def root_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return redirect('main:dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('main/', include('apps.main.urls')),
    path('organizaciones/', include('apps.orgs.urls')),
    path('users/', include('apps.users.urls')),
    path('planes/', include('apps.plans.urls')),
    path('', root_redirect),  # Redirección de la raíz al final
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)