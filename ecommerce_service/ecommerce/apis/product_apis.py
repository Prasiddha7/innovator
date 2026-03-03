from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ecommerce.models import Cart, CartItem, Commission, Order, OrderItem, Product
from ecommerce.serializers import CartItemSerializer, CartSerializer, CommissionSerializer, OrderSerializer, ProductSerializer
from ecommerce.permissions import IsAdminUser, IsCustomerUser, IsVendorOrAdmin, IsVendorUser


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsVendorOrAdmin()]

        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # def get_queryset(self):
    #     user = self.request.user

    #     if user.role == "ecommerce_vendor":
    #         return Product.objects.filter(created_by=user)

    #     if user.role == "admin":
    #         return Product.objects.all()

    #     return Product.objects.filter(is_active=True)

class CartViewSet(ModelViewSet):
   queryset = Cart.objects.all()
   serializer_class = CartSerializer
   permission_classes = [IsAuthenticated, IsCustomerUser]

   def get_queryset(self):
       return Cart.objects.filter(user=self.request.user)
   
   def perform_create(self, serializer):
       cart,created = Cart.objects.get_or_create(user=self.request.user)
       serializer.instance = cart
       serializer.save()

class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
   
class CommissionViewSet(ModelViewSet):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser, IsVendorUser]

    def get_queryset(self):
        if self.request.user.role == "vendor":
            return Commission.objects.filter(vendor__user=self.request.user)
        return Commission.objects.all()
    

class CheckoutViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def create_order(self, request):
        user = request.user
        cart_items = user.cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=400)

        order = Order.objects.create(customer=user, status="pending")
        total = 0

        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            line_total = item.quantity * item.product.price
            total += line_total

            # Commission
            if item.product.created_by.role == "ecommerce_vendor":
                vendor = item.product.created_by.vendor_profile
                percentage = vendor.commission_percentage
                commission_amount = (line_total * percentage) / 100

                Commission.objects.create(
                    vendor=vendor,
                    order_item=order_item,
                    commission_percentage=percentage,
                    commission_amount=commission_amount
                )

                vendor.total_earnings += commission_amount
                vendor.save()

            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        order.total_amount = total
        order.save()

        cart_items.delete()

        return Response({
            "message": "Order created",
            "order_id": order.id,
            "total": order.total_amount,
            "status": order.status
        })