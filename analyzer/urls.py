from django.urls import path
from . import views

urlpatterns = [
    path('', views.string_collection, name='string_collection'),           # GET /strings/
    path('create/', views.create_string, name='create_string'),            # POST /strings/create/
    path('filter-by-natural-language/', views.filter_natural, name='filter_natural'),
    path('<str:string_value>/', views.string_detail, name='string_detail'), # GET/DELETE /strings/{value}/
]
