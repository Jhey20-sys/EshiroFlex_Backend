from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Cart, Product, ShoeSize
from .serializers import CartSerializer, ProductSerializer  # ✅ Import ProductSerializer
from .models import Category
from .serializers import CategorySerializer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()
# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
# Cart ViewSet
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]  # Ensures only logged-in users access the cart

    def get_queryset(self):
        """Ensures that a user can only access their own cart."""
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assigns the logged-in user to the cart item."""
        serializer.save(user=self.request.user)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
# Add an item to the cart (Function-Based View)
@login_required  # ✅ Enforce authentication
@require_POST    # ✅ Ensure only POST requests are allowed
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_id = request.POST.get('size_id')
    size = get_object_or_404(ShoeSize, id=size_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user, product=product, product_size=size,
        defaults={'number_of_items': 1, 'total_price': product.price}
    )

    if not created:
        cart_item.number_of_items += 1
        cart_item.total_price = cart_item.number_of_items * product.price
        cart_item.save()

    return JsonResponse({"message": "Item added to cart", "cart_id": cart_item.id}, status=201)

# Remove an item from the cart
@login_required  # ✅ Enforce authentication
@require_POST    # ✅ Ensure only POST requests are allowed
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return JsonResponse({"message": "Item removed from cart"}, status=200)
