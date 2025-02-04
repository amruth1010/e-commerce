from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Accounts
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from .models import Address


class UserRegister(forms.ModelForm):
    password =forms.CharField(widget= forms.PasswordInput)
    confirm_password = forms.CharField(widget= forms.PasswordInput)
    class Meta:
        model= Accounts
        fields = ['first_name','last_name','email','password']

    def clean_email(self):
        email =self.cleaned_data.get('email')
        if Accounts.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")   
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password
    
class Emailauthentication(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class OtpForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label='OTP')




class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'phone_number']  # Ensure these match the fields in the model




# from django.contrib.auth.forms import AuthenticationForm
# from django import forms
# from django.contrib.auth import authenticate

# class CustomAdminAuthenticationForm(AuthenticationForm):
#     username = forms.EmailField(label="Email", max_length=254)

#     def clean(self):
#         email = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         if email and password:
#             self.user_cache = authenticate(self.request, email=email, password=password)
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)
#         return self.cleaned_data


