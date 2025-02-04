from django.urls import path
from .import views
app_name = 'dashboard'

urlpatterns = [
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('admin_dash/', views.admin_dash, name='admin_dash'),
    path('chart_data/', views.chart_data, name='chart_data'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
      
    
]


