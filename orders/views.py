
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import OrderForm
from orders.models import Order, OrderItem
from product.models import Products, SizeVariant
from django.contrib import messages
from django.db import transaction
from accounts.models import Cart, CartItem, Address
from django.contrib import messages
from django.db import transaction
from orders.forms import OrderForm,CouponForm
from orders.models import Order, OrderItem , Coupon
from accounts.models import Address
from django.contrib.auth.decorators import login_required
from .models import Order
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings


from django.urls import reverse

from .forms import OrderForm

import logging
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from .models import Order, OrderItem
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
import logging
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
from django.db import transaction
from .models import OrderItem
from .forms import OrderForm
from django.utils import timezone
import razorpay
from accounts.models import *


logger = logging.getLogger(__name__)

@csrf_exempt
@login_required(login_url='/login/')
def checkout(request):
    try:
        # Retrieve the cart and cart items for the current user
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('accounts:home')

        # Retrieve the applied coupon
        applied_coupon = cart.coupon

        total_amount = sum(
            (float(item.size_variant.price) if item.size_variant else float(item.product.price)) * item.quantity
            for item in cart_items
        )

        # Apply the coupon discount to the total amount
        if applied_coupon:
            discount_amount = float(applied_coupon.discount_amount)
            total_amount -= discount_amount

        print(request.POST)

            
        total_amount_in_paise = int(total_amount * 100)
        addresses = Address.objects.filter(user=request.user)     #Initializes the OrderForm to capture order details
        form = OrderForm(request.POST or None, user=request.user)

        if request.method == 'POST':
            if form.is_valid():
                try:
                    with transaction.atomic():
                        order = form.save(commit=False)
                        order.user = request.user
                        order.total_amount = total_amount
                        order.order_date = timezone.now()
                        
                        # Get payment method from form
                        payment_method = form.cleaned_data.get('payment_method')
                        order.payment_method = payment_method
                        
                        # Set initial payment status based on payment method
                        if payment_method == 'cod':  # Changed to match frontend value
                            order.payment_status = 'Pending'
                            order.status = 'Processing'
                        else:  # razorpay
                            order.payment_status = 'Pending'
                            order.status = 'Pending'
                            
                        if applied_coupon:
                            order.coupon = applied_coupon
                        order.save()

                        # Process cart items and update stock
                        for cart_item in cart_items:
                            size_variant = cart_item.size_variant
                            if size_variant:
                                if size_variant.stock < cart_item.quantity:
                                    messages.error(request, f"Not enough stock for {cart_item.product.product_name} in size {size_variant.size}.")
                                    order.delete()
                                    return redirect('orders:checkout')

                                OrderItem.objects.create(
                                    order=order,
                                    product=cart_item.product,
                                    size_variant=size_variant,
                                    quantity=cart_item.quantity,
                                    price=float(size_variant.price)
                                )
                                size_variant.stock -= cart_item.quantity
                                size_variant.save()
                            else:
                                if cart_item.product.stock < cart_item.quantity:
                                    messages.error(request, f"Not enough stock for {cart_item.product.product_name}.")
                                    order.delete()
                                    return redirect('orders:checkout')

                                OrderItem.objects.create(
                                    order=order,
                                    product=cart_item.product,
                                    quantity=cart_item.quantity,
                                    price=float(cart_item.product.price)
                                )
                                cart_item.product.stock -= cart_item.quantity
                                cart_item.product.save()

                        # Handle payment method specific logic
                        if payment_method == 'razorpay':
                            razorpay_order = create_razorpay_order(order)
                            if not razorpay_order:
                                logger.error(f"Razorpay order creation failed for order {order.order_number}")
                                order.delete()
                                return JsonResponse({
                                    'status': 'error',
                                    'message': "Failed to create payment order. Please try again."
                                }, status=400)

                            order.razorpay_order_id = razorpay_order['id']
                            order.save()
                            
                            # Clear the cart after order is created
                            empty_cart(cart, request)

                            confirmation_url = reverse('orders:order_confirmation', kwargs={'order_number': str(order.order_number)})
                            return JsonResponse({
                                'status': 'success',
                                'order_id': razorpay_order['id'],
                                'amount': total_amount_in_paise,
                                'key': settings.RAZORPAY_KEY_ID,
                                'redirect_url': confirmation_url
                            })
                        
                        # elif payment_method == 'wallet':
                        #     try:
                        #         req_user = Accounts.objects.get(email=request.user)
                        #         user_wallet = Wallet.objects.get(user=req_user)
                        #     except:
                        #         print('no user')
                        #         pass
                        #     if not user_wallet:
                        #         messages.error(request, 'Wallet Does Not Exist')
                        #         return redirect('orders:checkout')
                            
                        #     if user_wallet.balance < total_amount:
                        #         messages.error(request,'Not Enough Balance')
                        #         return redirect('orders:checkout')
                            
                        #     user_wallet.balance -= total_amount
                        #     user_wallet.save()
                            
                        #     empty_cart(cart, request)
                            
                        #     confirmation_url = reverse('orders:order_confirmation', kwargs={'order_number': str(order.order_number)})
                        #     return JsonResponse({
                        #         'status': 'success',
                        #         'payment_method': 'wallet',
                        #         'redirect_url': confirmation_url
                        #     })

                        else:  # COD
                            # Clear the cart after order is created
                            empty_cart(cart, request)

                            confirmation_url = reverse('orders:order_confirmation', kwargs={'order_number': str(order.order_number)})
                            return JsonResponse({
                                'status': 'success',
                                'payment_method': 'cod',
                                'redirect_url': confirmation_url
                            })

                except Exception as e:
                    logger.error(f"Checkout error: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=500)
            else:
                # Return form errors
                errors = {field: str(error[0]) for field, error in form.errors.items()}
                print("🚨 Form Errors:", form.errors)
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please enter the address:',
                    'errors': errors
                }, status=400)

        # For GET requests, render the checkout page
        context = {
            'cart_items': cart_items,
            'addresses': addresses,
            'total_amount': total_amount,
            'total_amount_in_paise': total_amount_in_paise,
            'form': form,
            'applied_coupon': None if not cart.coupon else cart.coupon,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        }
        return render(request, 'user_side/checkout.html', context)
    
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('accounts:home')


def empty_cart(cart, request):
    """Function to clear the user's cart after the order is successfully placed."""
    cart.items.all().delete()  # Delete all items in the cart
    cart.coupon = None  # Remove the applied coupon
    cart.save()
    request.session.pop('applied_coupon_code', None)  # Remove the coupon from session


def create_razorpay_order(order):
    """Create Razorpay order"""
    try:
        # Only create Razorpay order if payment method is razorpay
        if order.payment_method != 'razorpay':  # Changed to match frontend value
            return None
            
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(order.total_amount * 100)

        razorpay_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1',
            'notes': {
                'order_number': order.order_number
            }
        })

        return razorpay_order
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        return None


    
from django.shortcuts import render, get_object_or_404
from .models import Order
@login_required(login_url='/login/')
def order_confirmation(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        context = {
            'order': order,
        }
        return render(request, 'user_side/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('accounts:home')


@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    
    paginator = Paginator(orders, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_side/order_list.html', {'page_obj': page_obj})


from .models import Order

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required(login_url='/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'user_side/order_detail.html', {'order': order})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

@csrf_exempt
def payment_callback(request):
    try:
        # Get payment details from POST request
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Get the order
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            # Verify signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Fetch payment details to double check status
            payment = client.payment.fetch(payment_id)
            
            if payment['status'] == 'captured':
                # Update order status
                order.payment_status = 'Completed'
                order.status = 'Completed'
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.save()

                # Create success response with redirect URL
                redirect_url = reverse('orders:order_detail', kwargs={'order_id': order.id})
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment successful!',
                    'redirect_url': redirect_url,
                    'order_id': order.id
                })
            else:
                order.payment_status = 'Failed'
                order.save()
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Payment was not captured',
                    'redirect_url': reverse('orders:checkout')
                }, status=400)

        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'Failed'
            order.save()
            return JsonResponse({
                'status': 'failed',
                'message': 'Payment signature verification failed',
                'redirect_url': reverse('orders:checkout')
            }, status=400)

    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Order not found',
            'redirect_url': reverse('orders:checkout')
        }, status=404)
    except Exception as e:
        logger.error(f"Payment callback error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'redirect_url': reverse('orders:checkout')
        }, status=500)


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Order
from wallet.models import Wallet, WalletHistory

@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['Pending', 'Processing']:
        try:
            with transaction.atomic():
                order.status = 'Cancelled'

                # Check if the order was not already credited to the wallet
                if not order.credited_to_wallet:
                    # Get or create wallet
                    wallet = Wallet.get_or_create(request.user)
                    
                    # Use the add_money method from your Wallet model
                    wallet.add_money(order.total_amount)

                    order.credited_to_wallet = True

                order.save()

                # Restore stock for each item in the order
                for item in order.items.all():
                    size_variant = item.size_variant
                    if size_variant:
                        size_variant.stock += item.quantity
                        size_variant.save()
                
                messages.success(request, 'Your order has been cancelled successfully, and the amount has been credited to your wallet.')
        except Exception as e:
            messages.error(request, f'Error processing cancellation: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        messages.error(request, 'You cannot cancel this order.')
    
    return redirect('orders:order_detail', order_id=order.id)

from .forms import OrderStatusForm

@login_required
def admin_order_list(request):
    """View for listing all orders in the admin panel."""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_side/orderlist.html', {'orders': orders})

@login_required
def admin_order_detail(request, order_id):
    """View to show detailed order information."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_side/order_detail.html', {'order': order})

@login_required
def change_order_status(request, order_id):
    """View to allow admins to change the status of an order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders:admin_order_list')
    else:
        form = OrderStatusForm(instance=order)
    
    return render(request, 'admin_side/change_order_status.html', {'form': form, 'order': order})

@login_required
def cancel_order(request, order_id):
    """View to allow admins to cancel an order."""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in ['Delivered', 'Cancelled']:
        order.status = 'Cancelled'
        order.save()
    
    return redirect('orders:admin_order_list')

from django.shortcuts import render, get_object_or_404
from .models import Products  

@login_required
def admin_inventory_list(request):
    """View for listing all products and their stock levels."""
    products = Products.objects.all()
    return render(request, 'admin_side/inventory_list.html', {'products': products})

@login_required
def admin_edit_stock(request, product_id):
    """View to update stock for a product."""
    product = get_object_or_404(Products, id=product_id)
    
    if request.method == 'POST':
        new_stock = request.POST.get('stock')
        product.stock = int(new_stock)
        product.save()
        return redirect('orders:admin_inventory_list')
    
    return render(request, 'admin_side/edit_stock.html', {'product': product})


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from wallet.models import Wallet
from orders.models import Order

@login_required
@transaction.atomic
def return_order(request, order_id):
    # Fetch the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if the order is eligible for return
    if order.status != 'Delivered':
        messages.error(request, 'Only delivered orders can be returned.')
        return redirect('orders:order_detail', order_id=order.id)

    # Get or create the user's wallet
    wallet = Wallet.get_or_create(request.user)

    # Process refund
    refund_amount = order.total_amount  # Assuming `total_amount` is a field in your Order model
    wallet.add_money(refund_amount)

    # Update the order status
    order.status = 'Returned'
    order.save()

    # Success message
    messages.success(request, f'₹{refund_amount} has been credited to your wallet.')
    return redirect('orders:order_detail', order_id=order.id)



from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Cart
from .models import Coupon
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Coupon

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code.')
            return redirect('accounts:cart_detail')
        
        # Fetch the coupon
        coupon = Coupon.objects.filter(code=coupon_code).first()
        if not coupon:
            messages.error(request, 'Invalid coupon code.')
            return redirect('accounts:cart_detail')

        # Validate coupon
        if not coupon.is_valid():
            messages.error(request, 'The coupon is not valid.')
            return redirect('accounts:cart_detail')
        
        # Fetch the user's cart
        cart = get_object_or_404(Cart, user=request.user)
        
        # Check if the cart is empty
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty. Add items before applying a coupon.')
            return redirect('accounts:cart_detail')
        
        # Check if the coupon is already applied
        if cart.coupon and cart.coupon.code == coupon_code:
            messages.info(request, 'This coupon has already been applied.')
            return redirect('accounts:cart_detail')
        
        # Apply the coupon
        cart.apply_coupon(coupon)
        request.session['applied_coupon_code'] = coupon_code
        messages.success(request, f'Coupon "{coupon_code}" applied successfully.')

    return redirect('accounts:cart_detail')

from django.contrib import messages

def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully.')
            return redirect('orders:coupon_list')
        else:
            messages.error(request, 'Failed to create coupon. Please check the form fields.')
    else:
        form = CouponForm()
    return render(request, 'admin_side/create_coupon.html', {'form': form})



def delete_coupon(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully.')
        return redirect('orders:coupon_list')  # Redirect to coupon list view
    return render(request, 'admin_side/delete_coupon.html', {'coupon': coupon})


def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'admin_side/coupon_list.html', {'coupons': coupons})

def available_coupons(request):
    
    coupons = Coupon.objects.filter(is_active=True)  
    
    context = {
        'coupons': coupons,
    }
    return render(request, 'user_side/available_coupons.html', context)

from django.utils import timezone
from django.db.models import Sum, Count, F
from datetime import timedelta
from django.shortcuts import render
from .models import Order
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from django.shortcuts import render
from django.db.models import Sum, Count, F
from orders.models import Order  # Ensure you import your Order model

def sales_report(request):
    filter_type = request.GET.get('filter_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = timezone.now().date()

    # Handling different filter options
    if filter_type == 'daily':
        start_date, end_date = today, today
    elif filter_type == 'weekly':
        start_date, end_date = today - timedelta(days=7), today
    elif filter_type == 'monthly':
        start_date, end_date = today - timedelta(days=30), today
    elif filter_type == 'custom':
        if not start_date or not end_date:
            return render(request, 'admin_side/sales_report.html', {
                'error_message': "⚠️ Please select both Start Date and End Date.",
                'filter_type': filter_type
            })

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date > end_date:
                return render(request, 'admin_side/sales_report.html', {
                    'error_message': "⚠️ Start Date cannot be later than End Date.",
                    'filter_type': filter_type
                })
        except ValueError:
            return render(request, 'admin_side/sales_report.html', {
                'error_message': "⚠️ Invalid date format.",
                'filter_type': filter_type
            })
    else:
        start_date, end_date = today - timedelta(days=30), today  # Default to last 30 days

    # Ensure start_date and end_date are timezone-aware
    start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = make_aware(datetime.combine(end_date, datetime.max.time()))

    # Query orders based on the date range
    orders = Order.objects.filter(order_date__range=[start_date, end_date])

    total_sales = orders.aggregate(total_sales=Sum(F('total_amount') - F('discount')))['total_sales'] or 0
    total_discount = orders.aggregate(total_discount=Sum('discount'))['total_discount'] or 0
    order_count = orders.aggregate(order_count=Count('id'))['order_count'] or 0

    context = {
        'orders': orders,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'order_count': order_count,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
        'filter_type': filter_type,
    }

    return render(request, 'admin_side/sales_report.html', context)

from django.http import HttpResponse
from django.db.models import Sum
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import openpyxl

# Assuming your Order model has fields: id, total_amount, discount, order_date

def parse_date(date_str):
    """Helper function to parse a date string into a datetime object in 'YYYY-MM-DD' format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None  # Return None if the date string format is incorrect

def download_pdf(request):
    # Retrieve and parse the start and end dates from the URL parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    
    if not start_date or not end_date:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Fetch orders within the date range
    orders = Order.objects.filter(order_date__range=[start_date, end_date])

    # Aggregate the data for total sales, discount, and order count
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_discount = orders.aggregate(Sum('discount'))['discount__sum'] or 0
    order_count = orders.count()

    # Set up the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Initialize a PDF canvas
    pdf_canvas = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title and report summary
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(2 * inch, height - 1 * inch, "Sales Report")
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(1 * inch, height - 1.5 * inch, f"Report Period: {start_date_str} to {end_date_str}")
    pdf_canvas.drawString(1 * inch, height - 2 * inch, f"Total Sales: ${total_sales}")
    pdf_canvas.drawString(1 * inch, height - 2.5 * inch, f"Total Discount: ${total_discount}")
    pdf_canvas.drawString(1 * inch, height - 3 * inch, f"Total Orders: {order_count}")
    
    # Add a line separator
    pdf_canvas.line(0.5 * inch, height - 3.5 * inch, width - 0.5 * inch, height - 3.5 * inch)

    # Table headers for the order data
    pdf_canvas.drawString(1 * inch, height - 4 * inch, "Order ID")
    pdf_canvas.drawString(3 * inch, height - 4 * inch, "Total Amount")
    pdf_canvas.drawString(5 * inch, height - 4 * inch, "Discount")
    pdf_canvas.drawString(7 * inch, height - 4 * inch, "Order Date")
    
    
    y_position = height - 4.5 * inch
    for order in orders:
        pdf_canvas.drawString(1 * inch, y_position, str(order.id))
        pdf_canvas.drawString(3 * inch, y_position, f"${order.total_amount}")
        pdf_canvas.drawString(5 * inch, y_position, f"${order.discount}")
        pdf_canvas.drawString(7 * inch, y_position, order.order_date.strftime("%Y-%m-%d %H:%M"))
        y_position -= 0.25 * inch 

    
    pdf_canvas.save()
    
    return response

def download_excel(request):
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    
    if not start_date or not end_date:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    
    orders = Order.objects.filter(order_date__range=[start_date, end_date])

    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sales Report'

   
    ws.append(['Order ID', 'Total Amount', 'Discount', 'Order Date'])

    
    for order in orders:
        
        order_date_naive = order.order_date.replace(tzinfo=None)
        ws.append([order.id, order.total_amount, order.discount, order_date_naive])

    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date_str}_to_{end_date_str}.xlsx"'

    
    wb.save(response)

    return response


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse

def generate_invoice(request, order_id):
    # Fetch order details
    order = Order.objects.get(id=order_id)
    user_full_name = f"{order.user.first_name} {order.user.last_name}".strip()

    # Create a HTTP response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create the PDF canvas
    buffer = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Set up the title
    buffer.setFont("Helvetica-Bold", 18)
    buffer.drawString(200, height - 100, f"Invoice for Order #{order.id}")

    # Draw customer details
    buffer.setFont("Helvetica", 12)
    buffer.drawString(100, height - 140, f"Customer Name: {user_full_name}")
    buffer.drawString(100, height - 160, f"Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    buffer.drawString(100, height - 180, f"Shipping Address: {order.address}")

    # Table for order items
    data = [["Product", "Size", "Quantity", "Unit Price", "Total"]]
    for item in order.items.all():
        size = item.size_variant.size if item.size_variant else "N/A"  # Display size if available
        data.append([
            item.product.product_name,
            size,
            item.quantity,
            f"₹{item.price}",
            f"₹{item.quantity * item.price}"
        ])

    # Adding a total row
    total_amount = sum(item.quantity * item.price for item in order.items.all())
    data.append(["", "", "", "Total Amount", f"₹{total_amount}"])

    # Create and style table
    table = Table(data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw table
    table.wrapOn(buffer, width, height)
    table.drawOn(buffer, 100, height - 300)

    # Finalize PDF
    buffer.showPage()
    buffer.save()
    
    return response


from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, Address
from accounts.models import Address, Cart
@login_required
def cod_checkout(request):
    # Get user's cart and selected address
    user = request.user
    cart = Cart.objects.get(user=user)
    address = Address.objects.filter(user=user, is_default=True).first()

    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart.items.all())

    # Create a COD order
    order = Order.objects.create(
        user=user,
        address=address,
        total_amount=total_amount,
        status="Pending",
        payment_method="Cash on Delivery",
        payment_status="Completed",
        order_date=timezone.now(),
    )

    # Clear cart after order creation
    cart.items.all().delete()

    # Redirect to a confirmation page
    return redirect('orders:order_confirmation', order_id=order.id)



def test(request):
    return render(request,'user_side/test.html')