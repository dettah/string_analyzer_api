from django.urls import path
from . import views

urlpatterns = [
    path('', views.string_collection, name='string_collection'),  # GET /strings/ (list), POST /strings/ (create)
    path('filter-by-natural-language/', views.filter_natural, name='filter_natural'),  # GET /strings/filter-by-natural-language/?query=...
    path('<str:string_value>/', views.string_detail, name='string_detail'),  # GET /strings/{value}/, DELETE /strings/{value}/
]