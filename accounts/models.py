from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum, F


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email, **extra_fields)  #create regular usrs
        user.set_password(password)
        user.is_active = True
        user.date_joined = timezone.now()  #------- this is a cmanager for usr and superusr creation 
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True 
        user.date_joined = timezone.now()  
        user.save(using=self._db)
        return user    

class Accounts(AbstractBaseUser):
    email = models.EmailField(unique=True)   #in this model email is the u id for auth
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()                                 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        """Grant permissions only if the user is active and staff."""
        return self.is_active and self.is_staff

    def has_module_perms(self, app_label):
        """Grant app access only if the user is active and staff."""
        return self.is_active and self.is_staff
    

class Address(models.Model):
    user = models.ForeignKey('accounts.Accounts', on_delete=models.CASCADE) #Links an address to a specific user
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)      
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100)  
    is_default = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Format the address string representation
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

from orders.models import Coupon
class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    def get_total_price(self):
        # Calculate total price of items in the cart
        total_price = self.items.aggregate(
            total=Sum(
                F('quantity') * F('size_variant__price'),  # Use size_variant price if available
                output_field=models.DecimalField()
            )
        )['total']
        # Fallback to product price if size_variant price is not available
        if total_price is None:
            total_price = self.items.aggregate(
                total=Sum(
                    F('quantity') * F('product__price'),
                    output_field=models.DecimalField()
                )
            )['total']
        return total_price or 0   


    def apply_coupon(self, coupon):
        self.coupon = coupon
        self.save()     

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)   #Access all items in this cart using items
    product = models.ForeignKey('product.Products', on_delete=models.CASCADE)  
    size_variant = models.ForeignKey('product.SizeVariant', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # Ensure quantity does not exceed product stock
        if self.size_variant and self.quantity > self.size_variant.stock:
            self.quantity = self.size_variant.stock
        elif self.quantity > self.product.stock:
            self.quantity = self.product.stock
        super(CartItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in {self.cart.user.email}'s cart"