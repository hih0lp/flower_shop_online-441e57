from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import stripe
from .models import Flower, Category, Order, OrderItem
from .forms import SignUpForm, CheckoutForm
from .cart import Cart

# Public views

def index(request):
    categories = Category.objects.all()
    featured_flowers = Flower.objects.filter(is_available=True)[:8]
    return render(request, 'core/index.html', {
        'categories': categories,
        'featured_flowers': featured_flowers,
    })


def catalog(request):
    flowers = Flower.objects.filter(is_available=True)
    category_slug = request.GET.get('category')
    if category_slug:
        flowers = flowers.filter(category__slug=category_slug)
    q = request.GET.get('q')
    if q:
        flowers = flowers.filter(Q(name__icontains=q) | Q(description__icontains=q))
    paginator = Paginator(flowers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'core/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'query': q,
    })


def flower_detail(request, flower_id):
    flower = get_object_or_404(Flower, id=flower_id)
    return render(request, 'core/flower_detail.html', {'flower': flower})


def cart_view(request):
    cart = Cart(request)
    return render(request, 'core/cart.html', {'cart': cart})


def cart_add(request, flower_id):
    if request.method == 'POST':
        flower = get_object_or_404(Flower, id=flower_id)
        cart = Cart(request)
        cart.add(flower)
        return render(request, 'core/partials/cart_items.html', {'cart': cart})
    return HttpResponse(status=405)


def cart_update(request, flower_id):
    if request.method == 'POST':
        flower = get_object_or_404(Flower, id=flower_id)
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        cart.update(flower, quantity)
        return render(request, 'core/partials/cart_items.html', {'cart': cart})
    return HttpResponse(status=405)


def cart_remove(request, flower_id):
    if request.method == 'POST':
        flower = get_object_or_404(Flower, id=flower_id)
        cart = Cart(request)
        cart.remove(flower)
        return render(request, 'core/partials/cart_items.html', {'cart': cart})
    return HttpResponse(status=405)


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.get_total_price()
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    flower=item['flower'],
                    quantity=item['quantity'],
                )
            cart.clear()
            return redirect('payment', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'core/checkout.html', {'form': form, 'cart': cart})


@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/payment.html', {'order': order})


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = []
    for item in order.orderitem_set.all():
        line_items.append({
            'price_data': {
                'currency': 'rub',
                'product_data': {
                    'name': item.flower.name,
                },
                'unit_amount': int(item.flower.price * 100),
            },
            'quantity': item.quantity,
        })
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/payment/success/'),
            cancel_url=request.build_absolute_uri('/payment/cancel/'),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return JsonResponse({'error': str(e)})


def payment_success(request):
    return render(request, 'core/payment_success.html')


def payment_cancel(request):
    return render(request, 'core/payment_cancel.html')

# Auth views

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'core/order_history.html', {'orders': orders})

# Management views

@staff_member_required
def manage_flower_list(request):
    flowers = Flower.objects.all()
    return render(request, 'core/manage/flower_list.html', {'flowers': flowers})


@staff_member_required
def manage_flower_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')
        if name and price and category_id:
            category = Category.objects.get(id=category_id)
            flower = Flower.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                is_available=is_available,
                image=image,
            )
            return redirect('manage_flower_list')
    categories = Category.objects.all()
    return render(request, 'core/manage/flower_form.html', {'categories': categories})


@staff_member_required
def manage_flower_edit(request, flower_id):
    flower = get_object_or_404(Flower, id=flower_id)
    if request.method == 'POST':
        flower.name = request.POST.get('name')
        flower.description = request.POST.get('description')
        flower.price = request.POST.get('price')
        category_id = request.POST.get('category')
        flower.is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')
        if image:
            flower.image = image
        if category_id:
            flower.category = Category.objects.get(id=category_id)
        flower.save()
        return redirect('manage_flower_list')
    categories = Category.objects.all()
    return render(request, 'core/manage/flower_form.html', {'flower': flower, 'categories': categories})


@staff_member_required
def manage_flower_delete(request, flower_id):
    flower = get_object_or_404(Flower, id=flower_id)
    if request.method == 'POST':
        flower.delete()
        return redirect('manage_flower_list')
    return HttpResponse(status=405)
