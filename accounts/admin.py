from django.contrib import admin

from .models import Accounts

admin.site.register(Accounts)


# from django.contrib.admin import AdminSite
# from .forms import CustomAdminAuthenticationForm

# class CustomAdminSite(AdminSite):
#     login_form = CustomAdminAuthenticationForm
#     site_header = "Glamourista Admin"
#     site_title = "Admin Panel"
#     index_title = "Welcome to the Admin Panel"

# custom_admin_site = CustomAdminSite(name="custom_admin")

