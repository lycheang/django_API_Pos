from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
     CategoryViewSet, ProductViewSet, InventoryViewSet, SaleItemViewSet,UserViewSet,
     SaleViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet,basename='product')
router.register(r'inventories', InventoryViewSet, basename='inventory') 
router.register(r'saleitems', SaleItemViewSet, basename='saleitem')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # path('api/token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('api/', include(router.urls)),
    

]
