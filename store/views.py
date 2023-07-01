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
