"""
Hospital Admin App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-beds/', views.update_beds, name='update_beds'),
    path('update-facilities/', views.update_facilities, name='update_facilities'),
    path('update-pricing/', views.update_pricing, name='update_pricing'),
    path('update-insurances/', views.update_insurances, name='update_insurances'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('help-support/', views.help_support, name='help_support'),
]
