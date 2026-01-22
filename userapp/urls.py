"""
User App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'userapp'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search_hospitals, name='search'),
    path('results/', views.results, name='results'),
    path('compare/', views.compare_hospitals, name='compare'),
    path('ambulances/', views.ambulances, name='ambulances'),
    path('book-ambulance/', views.book_ambulance, name='book_ambulance'),
    path('live-availability/', views.live_hospital_availability, name='live_availability'),
]
