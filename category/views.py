
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from .forms import CategoryForm  

def list_categories(request):
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'admin_side/category_list.html', {'categories': categories})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category:list_categories')  
    else:
        form = CategoryForm()
    return render(request, 'admin_side/add_category.html', {'form': form})


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category:list_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_side/edit_category.html', {'form': form, 'category': category})


def toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id, is_deleted=False)
    category.is_active = not category.is_active  # Toggle active/inactive
    category.save()
    return redirect('category:list_categories')

# Soft delete category

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_deleted = True
    category.is_active = False  # Ensure it's also disabled when deleted
    category.save()
    return redirect('category:list_categories')


