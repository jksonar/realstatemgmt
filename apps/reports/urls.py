from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('financial/', views.financial_report, name='financial_report'),
    path('export/financial/', views.export_financial_report, name='export_financial'),
    path('custom-builder/', views.custom_report_builder, name='custom_report_builder'),
]