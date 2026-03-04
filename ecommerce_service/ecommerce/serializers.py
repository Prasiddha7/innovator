from django.db import transaction
from rest_framework import serializers
from .models import User, Cart, CartItem, Commission, OrderItem, Product, Order, VendorProfile, CustomerProfile

class UserSyncSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "role", "gender", "date_of_birth", "address", "phone_number"]



class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'is_approved', 'bio', 'commission_rate', 'commission_amount', 'total_earnings']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user']

class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_by', 'is_active', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    price = serializers.ReadOnlyField(source="product.price")
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "product_name", "price", "quantity", "total"]
        read_only_fields = ["cart"]

    def get_total(self, obj):
        return obj.product.price * obj.quantity
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total"]
        read_only_fields = ["user"]

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = "__all__"


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = "__all__"
#         read_only_fields = ["customer", "total_amount", "status"]

#     @transaction.atomic
#     def create(self, validated_data):
#         user = self.context["request"].user
#         cart = user.cart
#         cart_items = cart.items.all()

#         if not cart_items.exists():
#             raise serializers.ValidationError("Cart is empty")

#         order = Order.objects.create(customer=user)
#         total = 0

#         for item in cart_items:
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.price
#             )

#             line_total = item.product.price * item.quantity
#             total += line_total

#             # Commission
#             if item.product.created_by.role == "vendor":
#                 vendor = item.product.created_by.vendor_profile
#                 percentage = vendor.commission_percentage
#                 commission_amount = (line_total * percentage) / 100

#                 Commission.objects.create(
#                     vendor=vendor,
#                     order_item=order_item,
#                     commission_percentage=percentage,
#                     commission_amount=commission_amount
#                 )

#                 vendor.total_earnings += commission_amount
#                 vendor.save()

#             # Reduce stock
#             item.product.stock -= item.quantity
#             item.product.save()

#         order.total_amount = total
#         order.status = "pending"
#         order.save()

#         cart_items.delete()

#         return order

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["customer", "total_amount", "status"]

    def get_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            raise serializers.ValidationError({"cart": "Cart is empty"})

        order = Order.objects.create(customer=user, status="pending")
        total = 0

        for item in cart.items.select_related("product"):
            product = item.product

            # Stock validation
            if product.stock < item.quantity:
                raise serializers.ValidationError({
                    "stock": f"Only {product.stock} items available for {product.name}"
                })

            # Create order item
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            line_total = product.price * item.quantity
            total += line_total

            # Commission (if vendor product)
            if product.created_by.role == "ecommerce_vendor":
                vendor = product.created_by.vendor_profile
                percentage = vendor.commission_percentage or 0
                commission_amount = (line_total * percentage) / 100

                Commission.objects.create(
                    vendor=vendor,
                    order_item=order_item,
                    commission_percentage=percentage,
                    commission_amount=commission_amount
                )

                vendor.total_earnings += commission_amount
                vendor.save()

            # Reduce stock safely
            product.stock -= item.quantity
            product.save()

        order.total_amount = total
        order.status = "pending"
        order.save()

        # Clear cart
        cart.items.all().delete()

        return order
    
class CommissionSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order_item.order.id", read_only=True)
    product_name = serializers.CharField(source="order_item.product.name", read_only=True)
    quantity = serializers.IntegerField(source="order_item.quantity", read_only=True)
    selling_price = serializers.DecimalField(
        source="order_item.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    customer = serializers.CharField(source="order_item.order.customer.username", read_only=True)

    class Meta:
        model = Commission
        fields = [
            "id",
            "order_id",
            "product_name",
            "quantity",
            "selling_price",
            "customer",
            "commission_percentage",
            "commission_amount",
            "created_at",
        ]
        read_only_fields = fields