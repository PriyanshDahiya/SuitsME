from rest_framework import viewsets
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Product, UserInteraction
from django.contrib.auth.models import User
from .serializers import ProductSerializer
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserChangeForm
from django.http import JsonResponse
from .models import Product, LikedProduct
import json
from .models import Review
from django.urls import reverse
from .forms import CSVUploadForm
from .forms import ExcelUploadForm
from .utils import get_daily_quote
import csv
from django.http import HttpResponseForbidden
from django.db.models import Q
import random
from django.http import Http404
import pandas as pd
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from .forms import SignUpForm


# API ViewSet for Products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Home View
def home(request):
    daily_quote = get_daily_quote()
    max_price = request.GET.get('price', None)
    products = Product.objects.all()

    if max_price:
        try:
            max_price_value = float(max_price)
            products = products.filter(price__lte=max_price_value)
        except ValueError:
            pass

    paginator = Paginator(products, 1)  # Load one product initially
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/home.html', {
        'products': page_obj,
        'daily_quote': daily_quote
    })


@login_required
def get_next_product(request):
    max_price = request.GET.get('price', None)
    interacted_products = UserInteraction.objects.filter(user=request.user).values_list('product_id', flat=True)

    products = Product.objects.exclude(id__in=interacted_products)  # Exclude liked/disliked products

    if max_price:
        try:
            max_price_value = float(max_price)
            products = products.filter(price__lte=max_price_value)
        except ValueError:
            pass

    product = random.choice(products) if products else None  # Randomize product selection

    if product:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'product_url': product.product_url,
            'description': product.description
        }
        return JsonResponse({'product': product_data})
    else:
        return JsonResponse({'product': None})  # No more products left

@csrf_exempt
@login_required
def like_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        is_like = data.get('is_like')

        product = Product.objects.get(id=product_id)
        interaction, created = UserInteraction.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'interaction_type': 'like' if is_like else 'dislike'}
        )

        # Update interaction if it already exists
        if not created:
            interaction.interaction_type = 'like' if is_like else 'dislike'
            interaction.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
# Product Detail View
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        return render(request, 'products/product_detail.html', {'product': product})
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('home')  # Redirect to home if product doesn't exist

# Profile View (requires login)
@login_required
def profile(request):
    return render(request, 'products/profile.html')

# Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')  # Redirect to home after signup
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'products/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Redirect to home after login
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'products/login.html', {'form': form})

# Logout View
def custom_logout(request):
    logout(request)
    return redirect(reverse('login'))

# Edit Profile View (requires login)
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'products/edit_profile.html', {'form': form})

@csrf_exempt
def like_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        is_like = data.get('is_like')

        product = Product.objects.get(id=product_id)
        if is_like:
            # Save liked product
            LikedProduct.objects.get_or_create(user=request.user, product=product)
        else:
            # Optionally handle dislike logic (e.g., remove from liked products)
            LikedProduct.objects.filter(user=request.user, product=product).delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
@cache_page(60 * 15)  # Cache the page for 15 minutes (adjust as needed)
def liked_products(request):
    sort_by = request.GET.get('sort_by', 'date_desc')  # Default to Date Added
    liked_products = LikedProduct.objects.filter(user=request.user).select_related('product')

    # Apply sorting
    if sort_by == 'name_asc':
        liked_products = liked_products.order_by('product__name')
    elif sort_by == 'price_asc':
        liked_products = liked_products.order_by('product__price')
    elif sort_by == 'price_desc':
        liked_products = liked_products.order_by('-product__price')
    else:  # Default - Sort by most recently added
        liked_products = liked_products.order_by('-id')

    # Pagination: Show 20 products per page (adjust as needed)
    paginator = Paginator(liked_products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/liked_products.html', {'page_obj': page_obj})



from django.shortcuts import render

def about(request):
    return render(request, 'products/about.html', {'title': 'About Us'})


def review(request):
    if request.method == 'POST':
        content = request.POST.get('review')
        if content:
            Review.objects.create(content=content)
        return render(request, 'products/review.html', {'message': 'Thank you for your feedback!'})

    return render(request, 'products/review.html')

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                Product.objects.create(
                    name=row['product_name'],
                    price=row['mrp'],
                    description=row['description'],
                    image_url=row['feature_image'],  # Use the URL directly
                    product_url=row['pdp_url'],
                    category=row['category_name'],
                )

            return redirect('product_list')  # Redirect to a product list page or another page
    else:
        form = CSVUploadForm()

    return render(request, 'products/upload_csv.html', {'form': form})

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            
            try:
                # Read Excel file (handle .xls and .xlsx)
                data = pd.read_excel(excel_file)

                # Loop through each row and create Product objects
                for index, row in data.iterrows():
                    Product.objects.create(
                        name=row['product_name'],
                        price=row['mrp'],
                        description=row['description'],
                        image_url=row['feature_image'],  # Directly use the URL
                        product_url=row['pdp_url'],
                        category=row['category_name'],
                    )

                return redirect('product_list')  # Redirect to the product list or success page
            except Exception as e:
                print(f"Error: {e}")
                return render(request, 'products/upload_excel.html', {
                    'form': form,
                    'error': 'Failed to upload file. Please check the format.'
                })
    else:
        form = ExcelUploadForm()

    return render(request, 'products/upload_excel.html', {'form': form})

@login_required
def remove_from_wardrobe(request, liked_product_id):
    liked_product = get_object_or_404(LikedProduct, id=liked_product_id, user=request.user)
    
    if request.method == 'POST':
        liked_product.delete()
        return JsonResponse({'status': 'success'}, status=200)
    
    return HttpResponseForbidden("Invalid request")

@login_required
def view_user_wardrobe(request, username):
    user = get_object_or_404(User, username=username)
    liked_products = LikedProduct.objects.filter(user=user)
    return render(request, 'products/users_wardrobe.html', {
        'liked_products': liked_products,
        'user_profile': user
    })

@login_required
def autocomplete_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(Q(username__icontains=query))[:5]  # Limit to 5 suggestions
        results = [{'username': user.username} for user in users]
    else:
        results = []
    return JsonResponse(results, safe=False)


@login_required
def add_to_wardrobe(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # Check if the product is already liked by the current user
        already_liked = LikedProduct.objects.filter(user=request.user, product=product).exists()
        if not already_liked:
            LikedProduct.objects.create(user=request.user, product=product)
        return redirect('products/users_wardrobes.html')  # Redirect to the user's wardrobe page

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            return redirect('products/login.html')  # Redirect to the login page after successful signup
    else:
        form = SignUpForm()

    return render(request, 'products/signup.html', {'form': form})