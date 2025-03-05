from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, generics, status
from django.contrib.auth import get_user_model, logout
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import Product, Category, Order, Profile, Cart, Wishlist, Payment
from .serializers import (
    ProductSerializer, CategorySerializer, UserSerializer, RegisterSerializer,
    OrderSerializer, CartSerializer, WishlistSerializer, PaymentSerializer
)
from django.views.decorators.csrf import csrf_exempt
import json

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    - Admins can list, retrieve, update, and delete users.
    - Regular users can only view & update their own profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """ Define permissions dynamically based on action. """
        if self.action in ["list", "destroy"]:
            return [IsAdminUser()]  # Only admins can list or delete users
        return [IsAuthenticated()]  # Other actions require authentication

    def list(self, request):
        """ List all users (Admin only) """
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ Retrieve a user. Admins can retrieve any, users can retrieve their own. """
        if pk == "me":
            user = request.user  # Allow users to get their own profile using `/users/me/`
        else:
            user = get_object_or_404(User, pk=pk)

            if not request.user.is_staff and user != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """ Allow users to update their own info, admins can update any. """
        if pk == "me":
            user = request.user
        else:
            user = get_object_or_404(User, pk=pk)
            if not request.user.is_staff and user != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """ Admins can delete users. Users cannot delete their own accounts. """
        user = get_object_or_404(User, pk=pk)
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
### Category & Product Views
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

### Register & Login
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True  # Ensure users are active upon registration
        user.save()

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "email": user.email,
            "token": token.key,  # ✅ Return Token
        })

### Profile & Logout
class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        logout(request)
        return Response({"message": "User logged out successfully"}, status=200)


### Orders
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        number_of_items = serializer.validated_data['number_of_items']

        if product.stock < number_of_items:
            raise ValidationError({"error": "Not enough stock"})

        total_price = product.price * number_of_items
        serializer.save(user=self.request.user, total_price=total_price)

    def perform_update(self, serializer):
        try:
            instance = serializer.save()

            if not instance.product:
                raise ValidationError({"error": "Product not found"})

            instance.total_price = instance.product.price * instance.number_of_items
            instance.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


### Cart
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=request.data.get("product_id"))
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if not created:
            if product.stock > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart_item = get_object_or_404(Cart, user=request.user, id=kwargs["pk"])
        cart_item.delete()
        return Response({"message": "Product removed from cart"}, status=status.HTTP_204_NO_CONTENT)

### Wishlist
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=request.data.get("product_id"))
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        wishlist_item = get_object_or_404(Wishlist, user=request.user, id=kwargs["pk"])
        wishlist_item.delete()
        return Response({"message": "Product removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)

### Payments
class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def create(self, request):
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")

        if not order_id or not amount:
            return Response({"error": "order_id and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            user=request.user,
            order_id=order_id,
            amount=amount,
            status="completed",
            transaction_id=f"TXN{order_id}"
        )

        return Response({"message": "Payment successful", "payment_id": payment.id}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        payment = get_object_or_404(Payment, id=pk, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def refund(self, request, pk=None):
        payment = get_object_or_404(Payment, id=pk, user=request.user)

        if payment.status != "completed":
            return Response({"error": "Only completed payments can be refunded"}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = "refunded"
        payment.save()
        return Response({"message": "Refund successful", "payment_id": payment.id}, status=status.HTTP_200_OK)

class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)