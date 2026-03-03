from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .apis.admin_apis import VendorViewSet
from .apis.product_apis import CheckoutViewSet, ProductViewSet,CartViewSet,CartItemViewSet,OrderViewSet,CommissionViewSet
from .views import UserSyncView

router = DefaultRouter()
router.register("vendors", VendorViewSet)
router.register("products", ProductViewSet)
router.register("carts", CartViewSet, basename="cart")
router.register("cart-items", CartItemViewSet, basename="cart-items")
router.register("orders", OrderViewSet, basename="orders")
router.register("commissions", CommissionViewSet, basename="commissions")
router.register("checkout", CheckoutViewSet, basename="checkout")

urlpatterns = [
    path('internal/sync-user/', UserSyncView.as_view(), name='sync-user'),
    path('', include(router.urls))
]
