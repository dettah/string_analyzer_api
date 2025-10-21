# analyzer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_strings, name='list_strings'),  # GET /strings/
    path('filter-by-natural-language/', views.filter_natural, name='filter_natural'),
    path('create/', views.create_string, name='create_string'),  # POST /strings/create/
    path('<str:string_value>/', views.get_string, name='get_string'),
    path('<str:string_value>/delete/', views.delete_string, name='delete_string'),
]






# from django.urls import path
# from . import views

# urlpatterns = [
#     path('strings/', views.create_string),
#     path('strings/<str:string_value>/', views.get_string),
#     path('strings/filter-by-natural-language/', views.filter_natural),
#     path('strings/', views.list_strings),
#     path('strings/<str:string_value>/', views.delete_string),
# ]
