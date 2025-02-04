
from django.db import models
from product.models import Products 
from category.models import Category  
from accounts.models import Accounts  

class ProductOffer(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_percent}% off on {self.product.product_name}"

class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_percent}% off on {self.category.category_name}"

class ReferralOffer(models.Model):
    referrer = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_percent}% referral discount for {self.referred_user.email}"

