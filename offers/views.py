from django.shortcuts import render, redirect, get_object_or_404
from .models import CategoryOffer, ProductOffer
from product.models import Products
from category.models import Category
from .forms import CategoryOfferForm, ProductOfferForm


def list_offers(request):
    category_offers = CategoryOffer.objects.all()
    product_offers = ProductOffer.objects.all()
    return render(request, 'admin_side/offer_list.html', {
        'category_offers': category_offers,
        'product_offers': product_offers,
    })


def add_category_offer(request):
    categories = Category.objects.all() 
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offers:list_offers')
    else:
        form = CategoryOfferForm()
    return render(request, 'admin_side/category_offer_form.html', {
        'form': form,
        'categories': categories,  
    })


def edit_category_offer(request, offer_id):
    offer = get_object_or_404(CategoryOffer, id=offer_id)
    categories = Category.objects.all()  
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offers:list_offers')
    else:
        form = CategoryOfferForm(instance=offer)
    return render(request, 'admin_side/category_offer_form.html', {
        'form': form,
        'categories': categories,  
    })


def delete_category_offer(request, offer_id):
    offer = get_object_or_404(CategoryOffer, id=offer_id)
    if request.method == 'POST':
        offer.delete()
        return redirect('offers:list_offers')
    return render(request, 'admin_side/category_offer_confirm_delete.html', {'offer': offer})

# Add Product Offer
def add_product_offer(request):
    products = Products.objects.all()  # Fetch all products
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offers:list_offers')
    else:
        form = ProductOfferForm()
    return render(request, 'admin_side/product_offer_form.html', {
        'form': form,
        'products': products,  # Pass products to the template
    })

# Edit Product Offer
def edit_product_offer(request, offer_id):
    offer = get_object_or_404(ProductOffer, id=offer_id)
    products = Products.objects.all()  # Fetch all products
    if request.method == 'POST':
        form = ProductOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offers:list_offers')
    else:
        form = ProductOfferForm(instance=offer)
    return render(request, 'admin_side/product_offer_form.html', {
        'form': form,
        'products': products,  # Pass products to the template
    })

# Delete Product Offer
def delete_product_offer(request, offer_id):
    offer = get_object_or_404(ProductOffer, id=offer_id)
    if request.method == 'POST':
        offer.delete()
        return redirect('offers:list_offers')
    return render(request, 'admin_side/product_offer_confirm_delete.html', {'offer': offer})
