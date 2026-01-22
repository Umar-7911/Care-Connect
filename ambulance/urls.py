"""
Ambulance Admin App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ambulance'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-ambulances/', views.manage_ambulances, name='manage_ambulances'),
    path('update-pricing/', views.update_pricing, name='update_pricing'),
    path('service-area/', views.service_area, name='service_area'),
    path('bookings/', views.bookings, name='bookings'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('help-support/', views.help_support, name='help_support'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
