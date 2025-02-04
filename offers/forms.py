from django import forms
from .models import ProductOffer, CategoryOffer, ReferralOffer

class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_percent', 'start_date', 'end_date', 'is_active']

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount_percent', 'start_date', 'end_date', 'is_active']

class ReferralOfferForm(forms.ModelForm):
    class Meta:
        model = ReferralOffer
        fields = ['referrer', 'discount_percent', 'is_active']
 