from django.urls import path
from .import views
app_name = 'user_dash'

urlpatterns = [

    path('users/', views.list_users, name='list_users'),
    path('users/block/<int:user_id>/', views.block_user, name='user_block'),
    path('users/unblock/<int:user_id>/', views.unblock_user, name='user_unblock'),
    

]
