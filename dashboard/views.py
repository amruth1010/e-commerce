
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.http import HttpResponseRedirect


from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)

        admin = authenticate(request, username=username, password=password)

        if admin is not None:
            if admin.is_superuser:
                login(request, admin)
                return redirect('dashboard:admin_dash')
            else:
                messages.error(request, 'Please log in with your admin credentials to access the admin dashboard. If you encounter any issues, contact the support team.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_side/adminlogin.html')

from django.shortcuts import render
from django.db.models import Sum, Count
from orders.models import Order, OrderItem
from product.models import Products
from datetime import datetime
import json

def admin_dash(request):
    
    recent_orders = (
        Order.objects
        .select_related('user')
        .prefetch_related('items')
        .order_by('-order_date')[:10]
    )

    # Top 10 Best-Selling Products
    top_products = (
        OrderItem.objects
        .values('product__product_name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )

    # Top 10 Categories based on sales
    top_categories = (
        OrderItem.objects
        .values('product__product_category__name')
        .annotate(total_sales=Sum('quantity'))
        .order_by('-total_sales')[:10]
    )

    # Total orders summary
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='Completed').count()
    pending_orders = Order.objects.filter(status='Pending').count()
    top_products_json = json.dumps(list(top_products), default=str)
    top_categories_json = json.dumps(list(top_categories), default=str)

    context = {
        'recent_orders': recent_orders,
        'top_products': top_products,
        'top_categories': top_categories,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'top_products_json': top_products_json,
        'top_categories_json': top_categories_json,
    }

    return render(request, 'admin_side/admin_dash.html', context)


from django.db.models import Count
from orders.models import OrderItem

def get_top_products():
    return OrderItem.objects.values("product__name").annotate(total_sold=Count("product")).order_by("-total_sold")[:10]



from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from datetime import datetime, timedelta
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek


@csrf_exempt
def chart_data(request):
    
    filter_type = request.GET.get('filter', 'monthly')  
    # Get the data based on filter type
    if filter_type == 'yearly':
        data = (
            Order.objects
            .annotate(year=ExtractYear('order_date'))
            .values('year')
            .annotate(total_sales=Sum('total_amount'))
            .order_by('year')
        )
    elif filter_type == 'monthly':
        data = (
            Order.objects
            .annotate(month=ExtractMonth('order_date'))
            .values('month')
            .annotate(total_sales=Sum('total_amount'))
            .order_by('month')
        )
    elif filter_type == 'weekly':
        data = (
            Order.objects
            .annotate(week=ExtractWeek('order_date'))
            .values('week')
            .annotate(total_sales=Sum('total_amount'))
            .order_by('week')
        )

    # Prepare data in JSON format for charting
    chart_data = list(data)
    return JsonResponse(chart_data, safe=False)

@login_required(login_url='/login/')
def contact(request):
    return render(request, 'user_side/contact.html')

@login_required(login_url='/login/')
def about(request):
    return render(request, 'user_side/about.html')

