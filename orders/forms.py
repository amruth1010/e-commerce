
from django import forms
from .models import Order, Coupon
from accounts.models import *

class OrderForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        # ('wallet', 'Wallet'),
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    address = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        required=True
    )

    class Meta:
        model = Order
        fields = ['address', 'payment_method']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']            

from django import forms
from django.utils import timezone
from orders.models import Coupon  # Import your Coupon model

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'expiration_date', 'is_active']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')

        if expiration_date:
            # Convert expiration_date to a date-only format in case it's a datetime object
            expiration_date = expiration_date.date()

            # Convert timezone.now() to date to match expiration_date type
            today = timezone.now().date()

            if expiration_date < today:
                raise forms.ValidationError("⚠️ Expiration date cannot be in the past.")
        
        return expiration_date
