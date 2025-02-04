from django.urls import path
from .import views




app_name='offers'

urlpatterns = [

    path('offers/product/', views.list_offers, name='list_product_offers'),
    path('offers/product/add/', views.add_product_offer, name='add_product_offer'),
    path('offers/product/edit/<int:offer_id>/', views.edit_product_offer, name='edit_product_offer'),
    path('offers/product/delete/<int:offer_id>/', views.delete_product_offer, name='delete_product_offer'),
    path('offers/', views.list_offers, name='list_offers'),
    path('offers/category/add/', views.add_category_offer, name='add_category_offer'),
    path('offers/category/edit/<int:offer_id>/', views.edit_category_offer, name='edit_category_offer'),
    path('offers/category/delete/<int:offer_id>/', views.delete_category_offer, name='delete_category_offer'),
    path('offers/product/add/', views.add_product_offer, name='add_product_offer'),
    path('offers/product/edit/<int:offer_id>/', views.edit_product_offer, name='edit_product_offer'),
    path('offers/product/delete/<int:offer_id>/', views.delete_product_offer, name='delete_product_offer'),

    
]


   

