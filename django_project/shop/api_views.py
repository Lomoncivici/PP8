from rest_framework import viewsets, permissions
from .models import Product, Category, Tag
from .serializers import ProductSerializer, CategorySerializer, TagSerializer
from rest_framework.permissions import BasePermission

class IsAdminOrSeller(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (
                request.user.groups.filter(name__in=['Administrator', 'Seller']).exists() 
                or request.user.is_superuser
            )
        )

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrSeller]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSeller]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrSeller]