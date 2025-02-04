from django.urls import path
from .import views



app_name='category'

urlpatterns = [
    path('categories/', views.list_categories, name='list_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/toggle-status/<int:category_id>/', views.toggle_category_status, name='toggle_category_status'),

]


   

