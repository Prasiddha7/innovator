import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, role=None, **extra_fields):
        if role:
            extra_fields['role'] = role
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        
        # Auto-create Profiles based on role
        if role == "ecommerce_vendor":
            VendorProfile.objects.get_or_create(user=user, defaults={'id':user.id})
        elif role == "customer":
            CustomerProfile.objects.get_or_create(user=user, defaults={'id':user.id})
            
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, role="admin", **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        app_label = 'ecommerce'
    
    def __str__(self):
        return self.username
    

# --- PROFILES ---
class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class VendorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    is_approved = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}Vendor"
class CustomerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}Customer"
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id}"
    
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
class Commission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name="commissions"
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="commissions"
    )

    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.user.username} - {self.commission_amount}"
    
class VendorWallet(models.Model):
    vendor = models.OneToOneField(VendorProfile, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
