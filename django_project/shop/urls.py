from django.urls import path, reverse_lazy, include
from django.views.generic import DeleteView
from . import views
from django.contrib.auth import views as auth_views
from .models import Product, Category, Tag
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet, TagViewSet

app_name = 'shop'

urlpatterns = [
    # Открытые маршруты
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='shop:login'), name='logout'),
    path('register/', views.register, name='register'),

    # Закрытые маршруты (только для авторизованных пользователей)
    path('', views.ProductListView.as_view(), name='product-list'),
    path('product/add/', views.ProductCreateView.as_view(), name='product-add'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path(
        'product/<int:pk>/delete/',
        DeleteView.as_view(
            model=Product,
            template_name='shop/confirm_delete.html',
            success_url=reverse_lazy('shop:product-list')
        ),
        name='product-delete'
    ),

    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path(
        'category/<int:pk>/delete/',
        DeleteView.as_view(
            model=Category,
            template_name='shop/confirm_delete.html',
            success_url=reverse_lazy('shop:category-list')
        ),
        name='category-delete'
    ),
    path('category/<int:pk>/products/', views.ProductByCategoryListView.as_view(), name='product-by-category'),

    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path(
        'tag/<int:pk>/delete/',
        DeleteView.as_view(
            model=Tag,
            template_name='shop/confirm_delete.html',
            success_url=reverse_lazy('shop:tag-list')
        ),
        name='tag-delete'
    ),
    path('tag/<int:pk>/products/', views.ProductByTagListView.as_view(), name='product-by-tag'),

    path('api/', views.api_root, name='api_root'),  # HTML страница выбора API
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='cart-add'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='cart-remove'),
    path('checkout/', views.create_order, name='checkout'),
]

# DRF API
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api-product')
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'tags', TagViewSet, basename='api-tag')

urlpatterns += [path('api/', include(router.urls))]