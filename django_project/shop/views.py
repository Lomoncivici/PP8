from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product, Category, Tag, Order, OrderItem
from .forms import ProductForm, CategoryForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.crypto import get_random_string

# Главная страница (редирект на каталог или авторизацию)
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('shop:product-list')
    else:
        return redirect('login')

# Авторизация и регистрация
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:product-list')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

# ПРОФИЛЬ И API
@login_required
def api_root(request):
    return render(request, 'shop/api_root.html')

@login_required
def profile(request):
    return render(request, 'shop/profile.html')

# КОРЗИНА
@login_required
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('shop:cart')

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
    return redirect('shop:cart')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for pk, qty in cart.items():
        p = Product.objects.get(pk=pk)
        line_total = p.price * qty
        products.append({'product': p, 'qty': qty, 'line_total': line_total})
        total += line_total
    return render(request, 'shop/cart.html', {'products': products, 'total': total})

# ПРОДУКТЫ
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/catalog_list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(is_deleted=False)

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'shop/catalog_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_deleted=False)

class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/catalog_add.html'
    success_url = reverse_lazy('shop:product-list')
    permission_required = 'shop.add_product'

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/catalog_edit.html'
    success_url = reverse_lazy('shop:product-list')
    permission_required = 'shop.change_product'

class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'shop/confirm_delete.html'
    success_url = reverse_lazy('shop:product-list')
    permission_required = 'shop.delete_product'

# КАТЕГОРИИ
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'shop/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/category_add.html'
    success_url = reverse_lazy('shop:category-list')
    permission_required = 'shop.add_category'

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/category_edit.html'
    success_url = reverse_lazy('shop:category-list')
    permission_required = 'shop.change_category'

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'shop/confirm_delete.html'
    success_url = reverse_lazy('shop:category-list')
    permission_required = 'shop.delete_category'

class ProductByCategoryListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/catalog_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        cat = get_object_or_404(Category, pk=self.kwargs['pk'])
        return cat.products.filter(is_deleted=False)

# ТЕГИ
class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'shop/tag_list.html'
    context_object_name = 'tags'

class TagCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Tag
    fields = ['name', 'description']  # Или через форму
    template_name = 'shop/tag_add.html'
    success_url = reverse_lazy('shop:tag-list')
    permission_required = 'shop.add_tag'

class TagUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Tag
    fields = ['name', 'description']
    template_name = 'shop/tag_edit.html'
    success_url = reverse_lazy('shop:tag-list')
    permission_required = 'shop.change_tag'

class TagDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Tag
    template_name = 'shop/confirm_delete.html'
    success_url = reverse_lazy('shop:tag-list')
    permission_required = 'shop.delete_tag'

class ProductByTagListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/catalog_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        return tag.products.filter(is_deleted=False)

# ЗАКАЗЫ
@login_required
def create_order(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        full_name = request.POST.get('full_name')

        if not (address and phone and full_name):
            return render(request, 'shop/checkout.html', {'error': 'Заполните все поля!'})

        order_number = get_random_string(10).upper()
        order = Order.objects.create(
            order_number=order_number,
            address=address,
            phone=phone,
            full_name=full_name
        )

        for pk, qty in cart.items():
            product = Product.objects.get(pk=pk)
            OrderItem.objects.create(order=order, product=product, quantity=qty)

        request.session['cart'] = {}

        return render(request, 'shop/order_success.html', {'order': order})

    return render(request, 'shop/checkout.html')