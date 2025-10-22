from django.urls import path
from . import views

urlpatterns = [
    path('', views.strings, name='strings'),  # GET+POST /strings/
    path('filter-by-natural-language/', views.filter_natural, name='filter_natural'),
    path('<str:string_value>/', views.string_detail, name='string_detail'),
]