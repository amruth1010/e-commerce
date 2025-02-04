from django.db import models
from accounts.models import Accounts
from category.models import Category 

class SizeVariant(models.Model):
    size = models.CharField(max_length=50)

    def __str__(self):
        return self.size

class Products(models.Model):
    product_name = models.CharField(max_length=50, null=False)
    product_description = models.TextField(max_length=5000, null=False)
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    # product_brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnail_images', null=True, blank=True)

    highlights = models.TextField(max_length=1000, blank=True, null=True)  # Highlights or specs
    stock = models.PositiveIntegerField(default=0)  # Stock quantity
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Ratings (e.g., 4.5)
    review_count = models.PositiveIntegerField(default=0)  # Number of reviews
    size_variants = models.ManyToManyField(SizeVariant, related_name='products')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.product_name}"
    
class ProductImages(models.Model):
    product = models.ForeignKey(Products, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return f"Image for {self.product.product_name}"  

class Review(models.Model):
    product = models.ForeignKey(Products, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.user.email}" 

from django.conf import settings
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')






