from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, Category, ProductImages, SizeVariant
from .forms import ProductForm # Make sure to import the new form
from .utils import crop_and_resize
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

# List Products
@login_required
def product_list(request):
    products = Products.objects.all()
    return render(request, 'admin_side/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)  # Create product instance but don't save it yet
            product.save()  # Save the product instance

            # Handle size variants
            size_variants = form.cleaned_data.get('size_variants')
            if size_variants:
                product.size_variants.set(size_variants)  # Assign selected size variants to the product

            # Handle multiple images
            images = request.FILES.getlist('images')  # Get the list of uploaded images
            if images:
                for image in images:
                    try:
                        resized_image = crop_and_resize(image)  # Call your image resizing function
                        ProductImages.objects.create(product=product, image=resized_image)  # Create a ProductImages instance
                    except Exception as e:
                        print(f"Error processing image {image.name}: {e}")  # Log any errors
            else:
                print("No images were provided.")

            return redirect('product:product_list')  # Redirect to the product list after successful addition
        else:
            print("Form is invalid. Errors:", form.errors)  # Log form validation errors for debugging
    else:
        form = ProductForm()  # Create an empty form for GET requests

    categories = Category.objects.all()  # Fetch all categories for the dropdown
    return render(request, 'admin_side/add_product.html', {
        'form': form,
        'categories': categories
    })

@login_required
def edit_product(request, product_id):
    # Fetch the product using the provided product_id
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        # Initialize the form with the existing product instance
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            # Save the product instance but do not commit yet
            product = form.save(commit=False)
            product.save()

            # Handle size variants
            new_size_variants = form.cleaned_data.get('size_variants')  # Get selected size variants from the form

            if new_size_variants:
                product.size_variants.set(new_size_variants)  # Update the ManyToMany relationship

            # Handle multiple images
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    try:
                        resized_image = crop_and_resize(image)  # Your image resizing function
                        ProductImages.objects.create(product=product, image=resized_image)
                    except Exception as e:
                        print(f"Error processing image {image.name}: {e}")

            return redirect('product:product_list')  # Redirect after successful edit
        else:
            print("Form is invalid. Errors:", form.errors)
    else:
        # On GET request, populate the form with existing product data
        form = ProductForm(instance=product)

    categories = Category.objects.all()  # Fetch categories for the form

    return render(request, 'admin_side/edit_product.html', {
        'form': form,
        'categories': categories,
        'product': product
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.delete()
    return redirect('product:product_list')


from django.shortcuts import render, get_object_or_404, redirect
from .models import Products, ProductImages, SizeVariant
from .forms import ReviewForm
from offers.models import ProductOffer,CategoryOffer
from django.utils import timezone

@login_required
def product_detail(request, product_id):
    # Fetch product by ID
    product = get_object_or_404(Products, id=product_id)

    # Fetch product offer if it exists and is active
    product_offer = ProductOffer.objects.filter(
        product=product, 
        is_active=True, 
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()  # We use .first() to fetch the first matching offer (if any)

    # Fetch category offer if it exists and is active
    category_offer = CategoryOffer.objects.filter(
        category=product.product_category,
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()

    # Apply the discount if there's an active product or category offer
    discount = 0
    if product_offer:
        discount = product_offer.discount_percent
    elif category_offer:
        discount = category_offer.discount_percent

    # Calculate the discounted price
    discounted_price = product.price - (product.price * (discount / 100))

    # Check if user wants to show out-of-stock products (from query parameter)
    show_out_of_stock = request.GET.get('show_out_of_stock', '1')  # Default is to show all products

    # Fetch related products (limit to 4)
    if show_out_of_stock == '0':
        related_products = Products.objects.filter(
            product_category=product.product_category,
            stock__gt=0  # Only show products in stock
        ).exclude(id=product_id)[:4]
    else:
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
        'form': form,  # Always pass the review form
        'size_variants': size_variants,  # Pass the available size variants
        'product_images': product_images,  # Pass product images
        'show_out_of_stock': show_out_of_stock,  # Pass the filter state to the template
        'product_offer': product_offer,  # Pass the product offer
        'category_offer': category_offer,  # Pass the category offer
        'discounted_price': discounted_price,  # Pass the discounted price
        'discount': discount,  # Pass the discount percentage
    }
    return render(request, 'user_side/product_detail.html', context)

# views.py

@login_required
def search_view(request):
    query = request.GET.get('query')
    results = Products.objects.filter(product_name__icontains=query) if query else []
    return render(request, 'user_side/search_results.html', {'results': results, 'query': query})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Wishlist, Products

# Add to Wishlist
@login_required
def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Ensure user is logged in

    product = get_object_or_404(Products, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        return JsonResponse({'message': 'Product added to wishlist'}, status=200)
    else:
        return JsonResponse({'message': 'Product already in wishlist'}, status=200)

@login_required
# Remove from Wishlist
def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Ensure user is logged in

    product = get_object_or_404(Products, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist.exists():
        wishlist.delete()
        return JsonResponse({'message': 'Product removed from wishlist'}, status=200)
    else:
        return JsonResponse({'message': 'Product not in wishlist'}, status=404)
