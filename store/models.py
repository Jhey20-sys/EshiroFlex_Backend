from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

# Custom User Model
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_customer(self, email, full_name=None, cellphone_number=None, complete_address=None, password=None):
        """Creates and returns a customer (regular user)."""
        if not email:
            raise ValueError("Customers must have an email address")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            cellphone_number=cellphone_number,
            complete_address=complete_address,
            is_customer=True
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, cellphone_number, complete_address, password):
        """Creates and returns a superuser."""
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            cellphone_number=cellphone_number,
            complete_address=complete_address,
            is_staff=True,
            is_superuser=True
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    complete_address = models.TextField(blank=True, null=True)
    cellphone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Can access Django admin
    is_superuser = models.BooleanField(default=False)  # Has all permissions
    is_customer = models.BooleanField(default=True)  # Identifies regular users

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'cellphone_number', 'complete_address']

    def __str__(self):
        return self.email


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_token_expiry = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.user.email

# Auto-create Profile when a User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    product_size = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    number_of_items = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-calculate total price before saving."""
        self.total_price = self.product.price * self.number_of_items
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.product.name} x {self.number_of_items}"

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null = True, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.quantity})"

# Wishlist Model
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"

# Payment Model
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orders", null = True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    mode_of_payment = models.CharField(max_length=255, unique=True, null=True, blank=True)  
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Payment {self.id} - {self.status} ({self.amount})"
