from . import views
from django.urls import path

app_name = 'orders' 

urlpatterns = [

    path('checkout/', views.checkout, name='checkout'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/', views.admin_order_list, name='admin_order_list'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:order_id>/status/', views.change_order_status, name='change_order_status'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('inventory/', views.admin_inventory_list, name='admin_inventory_list'),
    path('inventory/<int:product_id>/edit/', views.admin_edit_stock, name='edit_stock'),
    path('order_confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('return/<int:order_id>/', views.return_order, name='return_order'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('create/', views.create_coupon, name='create_coupon'),
    path('coupons/delete/<int:id>/', views.delete_coupon, name='delete_coupon'),
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('available_coupons/', views.available_coupons, name='available_coupons'),
    # path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('create-order/', views.create_razorpay_order, name='create_order'),
    # path('payment-success/', views.payment_success, name='payment_success'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    path('download_excel/', views.download_excel, name='download_excel'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('checkout/cod/', views.cod_checkout, name='cod_checkout'),
    path('test',views.test,name='test'),
    
]


    

    

