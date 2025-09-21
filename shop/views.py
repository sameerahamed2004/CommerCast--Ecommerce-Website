from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, CartItem, Address, Order, OrderItem,Review
from .forms import AddressForm,ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from django.contrib import messages
from django.db.models import Avg
# --- Product list with optional category filter ---
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

# --- Product detail ---

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    already_reviewed = False
    review_form = None

    if request.user.is_authenticated:
        already_reviewed = reviews.filter(user=request.user).exists()
        if not already_reviewed:
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    new_review = review_form.save(commit=False)
                    new_review.product = product
                    new_review.user = request.user
                    new_review.save()
                    return redirect('product_detail', slug=slug)
            else:
                review_form = ReviewForm()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'already_reviewed': already_reviewed   
})
 
# --- Add to cart ---
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    messages.success(request, 'Item added to cart!')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('product_list')
# --- Cart detail ---
@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# --- Remove from cart ---
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart_detail')

# --- Address entry ---
@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')
    else:
        form = AddressForm()
    return render(request, 'shop/address_form.html', {'form': form})

# --- Checkout ---
@login_required
def checkout(request):
    # Always get the user's most recently saved address
    address = Address.objects.filter(user=request.user).last()
    
    if not address:
        # If user does not have any saved address, ask for it
        return redirect('add_address')
    
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            address=address,      # use latest address
            total_price=total_price
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            # stock update...
        cart_items.delete()
        return render(request, 'shop/checkout_success.html', {'total_price': total_price})

    return render(request, 'shop/checkout.html', {'total_price': total_price, 'address': address})

# --- Sign up (registration) ---
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

# --- Order history ---
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-date_placed')
    return render(request, 'shop/order_history.html', {'orders': orders})

# --- Product search ---
from django.db.models import Q

def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.none()
    return render(request, 'shop/product_search_result.html', {
        'products': products,
        'query': query
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

@login_required
@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-date_placed')

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserChangeForm(instance=user)

    context = {
        'user': user,
        'form': form,
        'orders': orders,
    }
    return render(request, 'shop/profile.html', context)

@login_required
def buy_now(request, product_id):
    from .models import Product, CartItem
    product = get_object_or_404(Product, id=product_id)
     # Clear all other cart items for this user for "true" buy now feel (optional)
    CartItem.objects.filter(user=request.user).delete()
    # Add this product (quantity=1) to cart for the user
    CartItem.objects.create(user=request.user, product=product, quantity=1)
    
    # Redirect to checkout directly
    return redirect('checkout')


@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    review_form = ReviewForm()

    if request.method == "POST":
        if not already_reviewed:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', slug=product.slug)
        else:
            # Optionally display message: Already reviewed
            pass

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
         'already_reviewed': already_reviewed
    }
    return render(request, 'shop/product_detail.html', context)