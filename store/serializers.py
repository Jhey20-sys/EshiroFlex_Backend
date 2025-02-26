from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Category, Cart

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Shoe Size Serializer (if needed)

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest ProductSerializer to include product details
    user = serializers.StringRelatedField()  # Display username instead of ID

        
    class Meta:
        model = Cart
        fields = '__all__'  # Ensures all fields are included
