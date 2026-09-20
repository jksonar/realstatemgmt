from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, LeadSourceViewSet, LeadActivityViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'lead-sources', LeadSourceViewSet)
router.register(r'lead-activities', LeadActivityViewSet)

app_name = 'leads'

urlpatterns = [
    path('', include(router.urls)),
]