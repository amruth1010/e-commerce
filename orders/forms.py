
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

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'expiration_date', 'is_active']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }