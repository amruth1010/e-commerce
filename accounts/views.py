from django.shortcuts import render
from .forms import OtpForm, UserRegister
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth import logout as auth_logout
import logging
from django.utils import timezone
from product.models import *
from .forms import Emailauthentication,AddressForm
from accounts.models import Address
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from product.models import Products
from category.models import Category 
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from accounts.models import *
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# Create your views here.

logger = logging.getLogger(__name__)
User = get_user_model()
 

def home(request):
    # Get only non-deleted and active categories
    categories = Category.objects.filter(is_deleted=False, is_active=True)

    # Get only active products belonging to active and non-deleted categories
    products = Products.objects.filter(
        product_category__is_active=True, 
        product_category__is_deleted=False, 
        is_active=True
    )

    # Get the sort option from the request, default to 'new_arrivals'
    sort_by = request.GET.get('sort', 'new_arrivals')
    selected_category = request.GET.get('category')  # Get the selected category from the request
    
    if selected_category:
        products = products.filter(product_category__id=selected_category)  # Filter products by category

    # Sorting options dictionary for better readability
    sorting_options = {
        'new_arrivals': '-created_at',
        'popularity': '-review_count',
        'price_low_to_high': 'price',
        'price_high_to_low': '-price',
        'average_ratings': '-average_rating',
        'featured': '-average_rating',
        'a_to_z': 'product_name',
        'z_to_a': '-product_name'
    }

    # Apply sorting if the selected option exists
    if sort_by in sorting_options:
        products = products.order_by(sorting_options[sort_by])

    context = {
        'products': products,
        'categories': categories,
        'sort_by': sort_by,  
        'selected_category': selected_category, 
    }
    return render(request, 'user_side/home.html', context)


def login(request):
    if request.user.is_authenticated:   #if the user is already logged in
        return redirect('accounts:home')
    
    if request.method == 'POST':
        form = Emailauthentication(request, data=request.POST)
        logger.debug(f"Form Valid: {form.is_valid()}")  # Debug statement
        
        if form.is_valid():
            user = form.get_user()
            logger.debug(f"Authenticated User: {user}")
            
            if user and user.is_active and not user.is_blocked:
                auth_login(request, user)
                messages.success(request, 'Account Activated Successfully')
                # request.session['user']={
                   
                #    'email':user.email,
                #    'isActive':user.is_active,
                #      }
                return redirect('accounts:home')
            else:
                messages.error(request, 'Account is inactive or blocked.')
        
        else:
            logger.debug(f"Form Errors: {form.errors}")
            messages.error(request, 'Invalid credentials. Please try again.')

    form = Emailauthentication()
    return render(request, 'user_side/login.html', {'form': form})

def logout(request):
    auth_logout(request)  #it clear the session and logut
    return redirect('accounts:home')



def signup(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')
    
    if request.method == 'POST':

        forms = UserRegister(request.POST)
        if forms.is_valid():
            User_data=forms.save(commit=False)
            User_data.is_active =False


            request.session['user_data']= {
                'first_name': User_data.first_name,
                'last_name': User_data.last_name,     #Temporarily stores user data for the verification process
                'email': User_data.email,
                'password': forms.cleaned_data.get('password')
            }

         #gerenate otp
            otp = get_random_string(length=6, allowed_chars='1234567890')
            print(otp)
            request.session['otp'] = otp   

            subject = 'Your OTP Code'
            message = f"""
            Dear {User_data.first_name},

            Welcome to Glamourista!
            Thank you for joining our fashion community. We are thrilled to have you on board and can't wait for you to explore our latest collections and exclusive offers.

            To complete your registration, please verify your email address using the One-Time Password (OTP) provided below:

            Your OTP: {otp}

            Enter this OTP on the website to verify your account and get started.

            If you have any questions or need assistance, feel free to reach out to our support team at support@Glamourista.com.

            Stay stylish!

            Best regards,
            The Glamourista Team
            """
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [User_data.email]
            
            send_mail(subject, message, email_from, recipient_list)  # it sends this email to the user 

            messages.success(request, 'An Otp send to email. Please verify to complete registration')
            return redirect('accounts:verify_otp')
    
    forms = UserRegister()
    return render(request, 'user_side/signup.html', {'forms':forms})

        
def verify_otp(request):
    if request.method=='POST':
        forms=OtpForm(request.POST)
        if forms.is_valid():
            otp = forms.cleaned_data.get('otp')   # retrive the otp from the form
            if otp == request.session.get('otp'):
                
                user_data = request.session.get('user_data')   # if the OTP is correct save  user data
                email = user_data.get('email')
                try:
                    
                    if Accounts.objects.filter(email=email).exists():    # Check if a user  email already exists in the db 
                        user = Accounts.objects.get(email=email)
                        messages.warning(request, 'User with this email already exists. Logging you in.')
                    else: 
                        user = Accounts.objects.create(                   # create a new accountt if email not exists 
                            first_name=user_data.get('first_name'),
                            last_name=user_data.get('last_name'),
                            email=email,                         
                        )
                        user.set_password(user_data.get('password'))
                        user.is_active = True
                        user.save()

                        
                        del request.session['user_data'] # Clear the session data
                        del request.session['otp']

                    return redirect('accounts:login')
                except IntegrityError:
                    messages.error(request, 'An error occurred while creating the user. Please try again.')
            else:
                messages.error(request, 'Invalid OTP')
                forms.add_error('otp', 'Invalid OTP')
    else:
        forms= OtpForm()
        return render(request, 'user_side/verify_otp.html', {'forms': forms})



def resend_otp(request):
    user_data = request.session.get('user_data')
    if user_data:
        otp = get_random_string(length=6, allowed_chars='1234567890')
        logger.debug(f"Generated OTP: {otp}")  # Debug 

        otp_generation_time = timezone.now().isoformat()
        logger.debug(f"OTP Generation Time: {otp_generation_time}")  

        print(otp)

        request.session['otp'] = otp
        request.session['otp_generation_time'] = otp_generation_time

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user_data['email']],
                fail_silently=False,
            )
            messages.success(request, 'A new OTP has been sent to your email.')
        except Exception as e:
            logger.error(f"Error sending email: {e}")  
            messages.error(request, 'Failed to send OTP. Please try again later.')
    else:
        messages.error(request, 'User data not found. Please register again.')
    return redirect('accounts:verify_otp')



@login_required(login_url='/login/')
def userdash(request):
    user = request.user.id  
    user_data = Accounts.objects.get(id=user)   #retrive user data by id
    return render(request, 'user_side/userdash.html', {'user_data': user_data})


def demo_login(request):
    demo_user = User.objects.get(email='demo@example.com')  
    auth_login(request, demo_user)

    return redirect('accounts:home')

@login_required(login_url='/login/')
def edit_profile(request):
    user = request.user  

    if request.method == 'POST':
        # Get the updated data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Update the user information
        user.first_name = first_name
        user.last_name = last_name
        user.save()  

        return redirect('accounts:userdash')

    return render(request, 'user_side/edit_profile.html', {'user_data': user})



@login_required(login_url='/login/')  
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            print(request.user)
            address.user = request.user  
            print(address.user)
            address.save()
            return redirect('/userdash')  
        else:
            print("User is not authenticated")
    else:
        form = AddressForm()
    return render(request, 'user_side/add_address.html', {'form': form})

    

@login_required(login_url='/login/')
def edit_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('accounts:userdash')
    else:
        form = AddressForm(instance=address)
    return render(request, 'user_side/edit_address.html', {'form': form})


@login_required(login_url='/login/')
def delete_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('accounts:userdash')
    return render(request, 'user_side/delete_address.html', {'address': address})


User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)  # Check if user exists
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n{link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset email has been sent.')
        except User.DoesNotExist:
            messages.error(request, 'No account associated with this email.')
        
        return redirect('accounts:forgot_password')

    return render(request, 'user_side/forgot_password.html')

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                user.password = make_password(new_password)  # Hash the password
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')

        return render(request, 'user_side/password_reset_confirm.html', {'valid_link': True})
    else:
        messages.error(request, 'This link is invalid or has expired.')
        return render(request, 'user_side/password_reset_confirm.html', {'valid_link': False})



@login_required(login_url='/login/')
def add_to_cart(request, product_id, size_variant_id=None):
    product = get_object_or_404(Products, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add logic to get size_variant if applicable
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if size_variant_id:
        cart_item.size_variant_id = size_variant_id

    # Check stock and increase quantity
    if cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()
    else:
        
        pass

    return redirect('accounts:cart_detail')



from django.shortcuts import get_object_or_404, render
from .models import Cart
from orders.models import Coupon

@login_required(login_url='/login/')
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    # Calculate the total price of the cart items
    total_price = sum(item.quantity * (item.size_variant.price if item.size_variant else item.product.price) for item in cart_items)

    # Initialize variables for coupon handling
    discount_amount = 0
    coupon_code = request.session.get('applied_coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount_amount = coupon.discount_amount
        except Coupon.DoesNotExist:
            coupon_code = None

    # Calculate the new total after applying the coupon
    new_total_price = total_price - discount_amount
    if new_total_price < 0:
        new_total_price = 0

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'new_total_price': new_total_price,
        'coupon_code': coupon_code,
    }
    return render(request, 'user_side/cart_detail.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import CartItem

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem

from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from .models import CartItem  # assuming CartItem model is imported

def update_cart_item_quantity(request, item_id):
    if request.method == 'POST':
        # Get the CartItem instance
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        new_quantity = int(request.POST.get('quantity', 1))

        # Check stock availability for the product or size variant
        if cart_item.size_variant:
            available_stock = cart_item.size_variant.stock
        else:
            available_stock = cart_item.product.stock

        # If requested quantity exceeds stock, return an error message
        if new_quantity > available_stock:
            return JsonResponse({
                'success': False,
                'error': f"Only {available_stock} items left in stock."
            })

        # Update the cart item with the new quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        # Calculate item total price
        item_total = cart_item.quantity * (
            cart_item.size_variant.price if cart_item.size_variant else cart_item.product.price
        )

        # Calculate the total price of all items in the cart
        total_price = cart_item.cart.items.aggregate(
            total=Sum(
                F('quantity') * F('size_variant__price') if cart_item.size_variant else F('quantity') * F('product__price'),
                output_field=models.DecimalField()
            )
        )['total'] or 0

        # Send the updated item total and cart total price in the response
        return JsonResponse({
            'success': True,
            'item_total': f"{item_total:.2f}",
            'total_price': f"₹{total_price:.2f}"
        })

    # Return error if the request method is not POST
    return JsonResponse({'success': False, 'error': "Invalid request method."})




@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    
    cart_item = get_object_or_404(CartItem, id=item_id)

    
    cart_item.delete()

    # If the request is AJAX, return a JSON response
    if request.is_ajax():
        # Retrieve remaining cart items for calculating the total price
        cart_items = CartItem.objects.filter(cart=cart_item.cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'total_price': total_price,
            'total_items': cart_items.count(),
            'message': 'Item removed from cart successfully.'
        })

    
    return redirect('accounts:cart_detail')



