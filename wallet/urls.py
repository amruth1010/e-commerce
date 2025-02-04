from django.urls import path
from .import views

app_name = 'wallet'

urlpatterns = [

    path('wallet_detail/', views.wallet_detail, name='wallet_detail'),
    path('refund/<int:order_id>/', views.process_refund, name='process_refund'),

    
]
