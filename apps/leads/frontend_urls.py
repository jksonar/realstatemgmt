from django.urls import path
from . import frontend_views

app_name = 'leads_frontend'

urlpatterns = [
    # Lead views
    path('', frontend_views.LeadListView.as_view(), name='lead-list'),
    path('<int:pk>/', frontend_views.LeadDetailView.as_view(), name='lead-detail'),
    path('create/', frontend_views.LeadCreateView.as_view(), name='lead-create'),
    path('<int:pk>/edit/', frontend_views.LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete/', frontend_views.LeadDeleteView.as_view(), name='lead-delete'),
    path('reports/', frontend_views.LeadReportView.as_view(), name='lead-reports'),
    
    # Lead activity views
    path('<int:lead_id>/add-activity/', frontend_views.add_lead_activity, name='add-activity'),
    path('<int:lead_id>/schedule-follow-up/', frontend_views.schedule_follow_up, name='schedule-follow-up'),
    path('<int:lead_id>/update-status/', frontend_views.update_lead_status, name='update-status'),
    
    # Lead source views
    path('sources/', frontend_views.LeadSourceListView.as_view(), name='lead-source-list'),
    path('sources/create/', frontend_views.create_lead_source, name='lead-source-create'),
    path('sources/<int:pk>/edit/', frontend_views.update_lead_source, name='lead-source-update'),
    path('sources/<int:pk>/delete/', frontend_views.LeadSourceDeleteView.as_view(), name='lead-source-delete'),
    
    # Export/Import views
    path('export/', frontend_views.export_leads, name='lead-export'),
    path('import/', frontend_views.import_leads, name='lead-import'),
]