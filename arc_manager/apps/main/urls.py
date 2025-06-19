from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('test-ses/', views.test_ses_view, name='test_ses'),
]