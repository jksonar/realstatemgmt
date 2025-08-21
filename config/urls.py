from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('properties/', include('apps.properties.urls')),
    path('tenants/', include('apps.tenants.urls')),
    path('leases/', include('apps.leases.urls')),
    path('payments/', include('apps.payments.urls')),
    path('maintenance/', include('apps.maintenance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)