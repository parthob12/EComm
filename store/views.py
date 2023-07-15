from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import Product, Cart, CartItem

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_list')

def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    return render(request, 'store/cart.html', {'cart': cart})

# views.py

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'registration/profile.html')


# views.py

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


# views.py

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    if request.method == 'POST':
        # Process the payment using Stripe
        token = request.POST['stripeToken']
        amount = 1000  # Adjust the amount as needed
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Payment for Order',
                source=token,
            )
            if charge.status == 'succeeded':
                # Create an order record in your database
                order = Order.objects.create(user=request.user, total_amount=amount)
                # Add products to the order
                for item in request.user.cart.cartitem_set.all():
                    order.products.add(item.product)
                # Clear the user's cart
                request.user.cart.cartitem_set.all().delete()
                return redirect('order_success')
            else:
                # Handle payment failure
                pass
        except stripe.error.CardError:
            # Handle card errors
            pass
    return render(request, 'store/checkout.html')
