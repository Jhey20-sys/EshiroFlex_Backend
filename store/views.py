from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .models import Product, Category

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        from .serializers import CategorySerializer
        return CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        from .serializers import ProductSerializer
        return ProductSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        from .serializers import UserSerializer
        return UserSerializer
