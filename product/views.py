from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, Category, ProductImages, SizeVariant
from .forms import ProductForm # Make sure to import the new form
from .utils import crop_and_resize
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from .utils import validate_image


@login_required(login_url='/login/')
def product_list(request):
    products = Products.objects.all()
    return render(request, 'admin_side/product_list.html', {'products': products})



from django.core.exceptions import ValidationError
from django.contrib import messages

@login_required(login_url='/login/')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()  # Save the product first to get the ID

            # Handle size variants
            size_variants = form.cleaned_data.get('size_variants')    
            if size_variants:
                product.size_variants.set(size_variants)

            # Handle images properly
            images = request.FILES.getlist('images')  # Get multiple uploaded images
            for image in images:
                ProductImages.objects.create(product=product, image=image)  # Save each image

            messages.success(request, "Product added successfully.")
            return redirect('product:product_list')
        else:
            messages.error(request, "Form is invalid. Please check the errors below.")
    else:
        form = ProductForm()

    categories = Category.objects.all()
    return render(request, 'admin_side/add_product.html', {
        'form': form,
        'categories': categories
    })


from django.contrib import messages
from django.core.exceptions import ValidationError

@login_required(login_url='/login/')
def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)  # Fetch the product

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Handle size variants
            new_size_variants = form.cleaned_data.get('size_variants')
            if new_size_variants:
                product.size_variants.set(new_size_variants)

            # Handle deleting existing images
            if 'delete_images' in request.POST:
                image_ids_to_delete = request.POST.getlist('delete_images')
                ProductImages.objects.filter(id__in=image_ids_to_delete).delete()

            # Handle new images
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    try:
                        validate_image(image)  # Validate the uploaded image
                        resized_image = crop_and_resize(image)
                        ProductImages.objects.create(product=product, image=resized_image)
                    except ValidationError as e:
                        messages.error(request, f"Validation error: {e}")
                    except Exception as e:
                        print(f"Error processing image {image.name}: {e}")

            messages.success(request, "Product updated successfully!")
            return redirect('product:product_list')
        else:
            messages.error(request, "Form is invalid. Please check the input.")

    else:
        form = ProductForm(instance=product)

    return render(request, 'admin_side/edit_product.html', {
        'form': form,
        'product': product,
    })


@login_required(login_url='/login/')
def delete_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.delete()
    return redirect('product:product_list')


from django.shortcuts import render, get_object_or_404, redirect
from .models import Products, ProductImages, SizeVariant
from .forms import ReviewForm
from offers.models import ProductOffer, CategoryOffer

from django.contrib.auth.decorators import login_required
from product.models import Products, SizeVariant, ProductImages


@login_required(login_url='/login/')
def product_detail(request, product_id):
    # Fetch product by ID
    product = get_object_or_404(Products, id=product_id)

    # Check for active product and category offers
    product_offer = ProductOffer.objects.filter(product=product, is_active=True).first()
    category_offer = CategoryOffer.objects.filter(category=product.product_category, is_active=True).first()

    # Apply the highest priority discount (Product offer first, then Category offer)
    if product_offer:
        discounted_price = product.price - (product.price * (product_offer.discount_percent / 100))
        offer_details = f"Product Offer: {product_offer.discount_percent}% off"
    elif category_offer:
        discounted_price = product.price - (product.price * (category_offer.discount_percent / 100))
        offer_details = f"Category Offer: {category_offer.discount_percent}% off"
    else:
        discounted_price = product.price  # No discount
        offer_details = None

    # Check if user wants to show out-of-stock products (from query parameter)
    show_out_of_stock = request.GET.get('show_out_of_stock', '1')  # Default is to show all products

    # Fetch related products (limit to 4)
    if show_out_of_stock == '0':
        # Filter out products with stock <= 0
        related_products = Products.objects.filter(
            product_category=product.product_category,
            stock__gt=0  # Only show products in stock
        ).exclude(id=product_id)[:4]
    else:
        # Show all products, including out-of-stock ones
        related_products = Products.objects.filter(
            product_category=product.product_category
        ).exclude(id=product_id)[:4]

    # Fetch parent category if it exists
    parent_category = product.product_category.parent if hasattr(product.product_category, 'parent') else None

    # Fetch size variants for the product
    size_variants = product.size_variants.all()

    # Fetch product images 
    product_images = ProductImages.objects.filter(product=product)

    # Handle form logic
    form = ReviewForm()  # Initialize form for the GET request

    if request.method == 'POST':
        if 'size' in request.POST:  # If the form is for selecting a size
            selected_size_id = request.POST.get('size')
            try:
                selected_size = SizeVariant.objects.get(id=selected_size_id)
                # Add any further logic for size selection 
                print(f"User selected size: {selected_size}")
            except SizeVariant.DoesNotExist:
                print("Selected size does not exist")

        else:  # If the form submission is for submitting a review
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product:product_detail', product_id=product.id)

    # Pass necessary context to the template
    context = {
        'product': product,
        'related_products': related_products,
        'category': product.product_category,
        'parent_category': parent_category,
        'form': form,  #review form
        'size_variants': size_variants,  #available size variants
        'product_images': product_images,  
        'show_out_of_stock': show_out_of_stock,  
        'discounted_price': discounted_price,  #calculated discounted price
        'offer_details': offer_details,  
    }
    return render(request, 'user_side/product_detail.html', context)



@login_required(login_url='/login/')
def search_view(request):
    query = request.GET.get('query')
    results = Products.objects.filter(product_name__icontains=query) if query else []
    return render(request, 'user_side/search_results.html', {'results': results, 'query': query})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Wishlist, Products

@login_required(login_url='/login/')
def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')  

    product = get_object_or_404(Products, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist.exists():
        wishlist.delete()
        return JsonResponse({'message': 'Product removed from wishlist'}, status=200)
    else:
        return JsonResponse({'message': 'Product not in wishlist'}, status=404)


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Wishlist, Products

@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Products, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        if created:
            return JsonResponse({'message': 'Product added to wishlist'})
        else:
            return JsonResponse({'message': 'Product already in wishlist'})
    return JsonResponse({'message': 'Invalid request method'}, status=400)

@login_required(login_url='/login/')
def wishlist(request):
    # Get all wishlist items for the current user
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    print(f"Found {wishlist_items.count()} wishlist items for user {request.user}")
    
    return render(request, 'user_side/wishlist.html', {
        'wishlist_items': wishlist_items
    })



from django.shortcuts import render
from .models import Products, Category


@login_required(login_url='/login/')
def shop(request):
    # Get only non-deleted and active categories
    categories = Category.objects.filter(is_deleted=False, is_active=True)

    # Get only active products belonging to active and non-deleted categories
    products = Products.objects.filter(
        product_category__isnull=False,  # Ensure product_category is NOT NULL
        product_category__is_active=True,  
        product_category__is_deleted=False,  
        is_active=True
    )

    # Handle search functionality
    search_term = request.GET.get('search', '')
    if search_term:
        products = products.filter(product_name__icontains=search_term)

    # Handle category filtering
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(product_category__id=selected_category)

    # Handle sorting
    sort_by = request.GET.get('sort', 'new_arrivals')
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

    if sort_by in sorting_options:
        products = products.order_by(sorting_options[sort_by])

    context = {
        'products': products,
        'categories': categories,
        'sort_by': sort_by,
        'selected_category': selected_category,
        'search_term': search_term,
    }

    return render(request, 'user_side/shop.html', context)


from accounts.models import Address
from accounts.forms import AddressForm

@login_required(login_url='/login/')
def mg(request):
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('product:mg')
    
    return render(request, 'user_side/base3.html', {
        'addresses': addresses,
    })