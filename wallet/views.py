from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Wallet, WalletHistory
from django.db.transaction import atomic

@login_required(login_url='/login/')
def wallet_detail(request):
    wallet = Wallet.get_or_create(request.user)
    transactions = WalletHistory.objects.filter(wallet=wallet)[:10]
    return render(request, 'user_side/wallet_detail.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required(login_url='/login/')
@atomic
def process_refund(request, order_id):
    from orders.models import Order  # Import your Order model
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        wallet = Wallet.get_or_create(request.user)
        
        refund_amount = Decimal(str(order.total_amount))  # Get refund amount from order
        
        # Add refund to wallet
        wallet.add_money(refund_amount)
        WalletHistory.objects.create(
            wallet=wallet,
            amount=refund_amount,
            transaction_type='REFUND',
            notes=f"Refund for Order #{order.id}"
        )
        
        # Update order status
        order.status = 'CANCELLED'  # Update based on your Order model
        order.save()
        
        messages.success(request, f'Refund of ₹{refund_amount} has been added to your wallet')
        return redirect('orders:order_detail', order_id=order.id)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('orders:order_list')
    except Exception as e:
        messages.error(request, 'Error processing refund')
        return redirect('orders:order_list')
