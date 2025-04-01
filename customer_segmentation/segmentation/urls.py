from django.urls import path
from . import views

app_name = 'segmentation'

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('process/', views.process_clusters, name='process'),
    # Add a root URL redirect to the upload page
    path('', views.upload_file, name='home'), 
]