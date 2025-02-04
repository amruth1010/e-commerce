from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name='accounts'

urlpatterns = [
   path('',views.home,name="home"),
   path('login/',views.login,name="login"),
   path('logout/',views.logout,name="logout"),
   path('signup/',views.signup,name="signup"),
   path('verify_otp/', views.verify_otp, name='verify_otp'),
   path('resend_otp/',views.resend_otp,name="resend_otp"),
   path('userdash/',views.userdash,name='userdash'),
   path('demo_login/', views.demo_login, name='demo_login'),
   path('edit_profile/',views.edit_profile, name='edit_profile'),
   path('add_address/',views.add_address,name='add_address'),
   path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
   path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
   path('forgot_password/', views.forgot_password, name='forgot_password'),
   path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
   path('cart/', views.cart_detail, name='cart_detail'),
   path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
   path('update/<int:item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
   path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   


]



