

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Accounts


def list_users(request):
    query = request.GET.get('search', '')
    if query:
        users = Accounts.objects.filter(email__icontains=query) | Accounts.objects.filter(first_name__icontains=query) | Accounts.objects.filter(last_name__icontains=query)
    else:
        users = Accounts.objects.all()
    return render(request, 'admin_side/admin_user.html', {'users': users})


def block_user(request, user_id):
    user = Accounts.objects.get(id=user_id)
    user.is_blocked = True
    user.save()
    messages.success(request, f'{user.email} has been blocked.')
    return redirect('user_dash:list_users')


def unblock_user(request, user_id):
    user = Accounts.objects.get(id=user_id)
    user.is_blocked = False
    user.save()
    messages.success(request, f'{user.email} has been unblocked.')
    return redirect('user_dash:list_users')


