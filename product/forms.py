from django import forms
from .models import Products,Category,ProductImages,SizeVariant

class ProductForm(forms.ModelForm):

    size_variants = forms.ModelMultipleChoiceField(
        queryset=SizeVariant.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True  
    )

    class Meta:
        model = Products
        fields = [
            'product_name', 
            'product_description', 
            'product_category', 
            'price', 
            'offer_price', 
            'thumbnail',
            'highlights',
            'stock',
            'average_rating',
            'review_count',
            'size_variants',
        ]

    product_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_deleted=False),
        empty_label="Select a category",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_category'].queryset = Category.objects.filter(is_deleted=False)


    def clean_offer_price(self):
        price = self.cleaned_data.get('price')
        offer_price = self.cleaned_data.get('offer_price')
        if offer_price and offer_price >= price:
            raise forms.ValidationError("Offer price must be less than the regular price.")
        return offer_price


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['image']


from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }


