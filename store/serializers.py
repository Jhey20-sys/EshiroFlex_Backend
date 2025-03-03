from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Category, Order, Cart, Wishlist
from .models import Payment
from rest_framework.authtoken.models import Token




User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'full_name', 'cellphone_number', 'complete_address', 'is_customer']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'cellphone_number', 'complete_address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_customer(**validated_data)
        token, _ = Token.objects.get_or_create(user=user)  # ✅ Generate token on signup
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)  # ✅ Generate or retrieve token
            return {
                "email": user.email,
                "token": token.key,  # ✅ Return Token instead of JWT
            }
        raise serializers.ValidationError("Invalid credentials")
    
# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Product
        fields = '__all__'

# Registration Serializer


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'product', 'product_id',
            'number_of_items', 'total_price', 'created_at'
        ]
        read_only_fields = ['total_price', 'created_at']  

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['user', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()

class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'added_at']
        read_only_fields = ['user']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'mode_of_payment']  