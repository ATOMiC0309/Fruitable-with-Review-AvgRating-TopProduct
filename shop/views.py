from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import Category, Product, Rating, Email, Review
from .forms import LoginForm, RegisterForm, EmailForm, ReviewForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Avg


# Create your views here.


class ProductList(ListView):
    model = Product
    template_name = 'shop/index.html'
    context_object_name = 'products'
    extra_context = {
        'categories': Category.objects.filter(parent=None),
        'title': "Barcha Produclar",
        'all_products': Product.objects.all(),
        'form': EmailForm()
    }

    def get_queryset(self):
        return Product.objects.filter(is_sale=0)


class AllProductList(ProductList):
    template_name = 'shop/all_products.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.exclude(is_sale=0)

        context['sale_products'] = products.order_by('-is_sale')[:3]
        high_avg_rating_product = Product.objects.annotate(avg_rating=Avg('rating__rating')).order_by(
            '-avg_rating').first()
        context['high_avg_rating'] = high_avg_rating_product
        return context


class ByIsSale(AllProductList):
    def get_queryset(self):
        return Product.objects.exclude(is_sale=0)


def detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    context = {
        'categories': Category.objects.filter(parent=None),
        'product': product,
        'products': Product.objects.filter(category=product.category),
        'form': EmailForm(),
        'reviews': Review.objects.filter(product=product),
        'is_sale_products': Product.objects.exclude(is_sale=0).order_by('-is_sale')[:6]
    }
    rating = Rating.objects.filter(post=product, user=request.user.id).first()  # Requestdan foydalanish
    product.user_rating = rating.rating if rating else 0
    return render(request, 'shop/detail.html', context=context)


def product_by_category(request, pk):
    category = Category.objects.get(pk=pk)
    products = Product.objects.filter(category=category)
    context = {
        'categories': Category.objects.filter(parent=None),
        'products': products,
        'all_products': Product.objects.all()
    }
    return render(request, 'shop/all_products.html', context=context)


def rate(request: HttpRequest, post_id: int, rating: int) -> HttpResponse:
    post = Product.objects.get(id=post_id)
    Rating.objects.filter(post=post, user=request.user).delete()
    post.rating_set.create(user=request.user, rating=rating)
    return detail(request, post_id)


def user_logout(request):
    """This is for logout"""

    logout(request)
    return redirect('login')


def user_login(request):
    """This is for login"""

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('index')

        if form.errors:
            messages.error(request, "Check that the fields are correct!")

    form = LoginForm()
    context = {
        'form': form,
        'title': 'Sign in'
    }
    return render(request, 'shop/login.html', context=context)


def user_register(request):
    """This is for sing up"""

    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "You can log in by entering your username and password.")
            return redirect('login')

        if form.errors:
            messages.error(request, "Check that the fields are correct!")

    form = RegisterForm()
    context = {
        'form': form,
        'title': 'Sign up'
    }
    return render(request, 'shop/register.html', context=context)


def user_email(request):
    form = EmailForm(data=request.POST)
    form.save()
    return redirect('index')


def save_review(request, product_pk):
    if request.user.is_authenticated:
        print(request.POST, "*"*300)
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            print(request.POST, "+"*300)
            product = Product.objects.get(pk=product_pk)
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            print(review, "-"*300)
            review.save()
            messages.success(request, "Feedback has been sent!")
            return redirect('detail', product_id=product_pk)

        messages.error(request, "Fields are invalid!")
        return redirect('detail', product_id=product_pk)
    else:
        messages.warning(request, "Please login first to comment!")
        return redirect('login')