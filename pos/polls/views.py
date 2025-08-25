from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponseForbidden
from polls.models import Category, Product, Inventory, SaleItem, User, Sale
from polls.serializers import (
    CategorySerializer, ProductSerializer, InventorySerializer,
    SaleItemSerializer, UserSerializer, UserCreateUpdateSerializer,
    SaleSerializer, MyTokenObtainPairSerializer, RefundSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from polls.permission import IsAdminRole, IsUserOrAdmin

# Get the custom User model
User = get_user_model()


# Custom pagination class for controlling page sizes
class ForPageNumberPagination(PageNumberPagination):
    page_size = 3  # Default number of items per page
    page_size_query_param = 'page_size'  # URL parameter to override page size
    max_page_size = 10  # Maximum allowed page size


# Custom JWT token obtain view with error handling
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Handle token generation with proper error handling
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return response


# User management viewset with custom actions and serializers
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Default queryset
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    pagination_class = ForPageNumberPagination  

    # Custom action to get all users without pagination
    @action(detail=False, methods=['get'], url_path='all')
    def get_all_users(self, request):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    # Determine which serializer to use based on action
    def get_serializer_class(self):
        # Use different serializer for create/update actions
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserSerializer

    # Custom create method to return proper response format
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        # Return user data with standard serializer after creation
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    # Custom update method to return proper response format
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)


# Category management viewset
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsUserOrAdmin]  # Custom permission class
    pagination_class = ForPageNumberPagination

    # Custom action to get all categories without pagination
    @action(detail=False, methods=['get'], url_path='all')
    def get_all_accounts(self, request):
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    # Automatically set created_by and updated_by fields
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    # Automatically update updated_by field
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# Product management viewset
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # More open permissions
    pagination_class = ForPageNumberPagination

    # Custom action to get all products without pagination
    @action(detail=False, methods=['get'], url_path='all')
    def get_all_accounts(self, request):
        product = Product.objects.all()
        serializer = self.get_serializer(product, many=True)
        return Response(serializer.data)

    # Automatically set created_by and updated_by fields
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    # Automatically update updated_by field
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# Inventory management viewset with validation
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]  # Requires authentication
    pagination_class = ForPageNumberPagination

    # Custom action to get all inventory records without pagination
    @action(detail=False, methods=['get'], url_path='all')
    def get_all_accounts(self, request):
        inventories = Inventory.objects.all()
        serializer = self.get_serializer(inventories, many=True)
        return Response(serializer.data)

    # Automatically set last_updated_by field
    def perform_create(self, serializer):
        serializer.save(last_updated_by=self.request.user)

    # Automatically update last_updated_by field
    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user)

    # Custom create method with product uniqueness validation
    def create(self, request, *args, **kwargs):
        # Check if product already has an inventory record
        product_id = request.data.get('product')
        if product_id and Inventory.objects.filter(product_id=product_id).exists():
            return Response(
                {'error': 'This product already has an inventory record'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


# SaleItem management viewset (basic implementation)
class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticated]  # Requires authentication
    pagination_class = ForPageNumberPagination

    @action(detail=False, methods=['get'], url_path='all')
    def get_all_accounts(self, request):
        saleitem = SaleItem.objects.all()
        serializer = self.get_serializer(saleitem, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


# Sale management viewset with complex refund functionality
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().prefetch_related('items', 'items__product')  # Optimized queryset
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]  # Requires authentication
    pagination_class = ForPageNumberPagination

    # Custom action to get all sales without pagination
    @action(detail=False, methods=['get'], url_path='all')
    def get_all_accounts(self, request):
        sales = Sale.objects.all()
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)

    # Automatically set created_by field
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # Standard create method
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # Custom refund action with transaction safety
    @action(detail=True, methods=['post'], url_path='refund')
    def refund(self, request, pk=None):
        sale = self.get_object()  # Get the sale being refunded
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refund_items = serializer.validated_data['items']

        # Use transaction to ensure atomicity
        with transaction.atomic():
            total_refund_amount = 0

            # Process each item in the refund request
            for item_data in refund_items:
                product = item_data['product']
                qty_to_refund = item_data['qty']

                try:
                    # Find the original sale item
                    sale_item = SaleItem.objects.get(sale=sale, product=product)
                except SaleItem.DoesNotExist:
                    return Response(
                        {"error": f"Product {product.id} not found in this sale."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validate refund quantity doesn't exceed sold quantity
                if qty_to_refund > sale_item.qty:
                    return Response(
                        {"error": f"Refund quantity for product {product.id} exceeds sold quantity."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update sale item quantity
                sale_item.qty -= qty_to_refund
                refund_value = qty_to_refund * sale_item.price
                total_refund_amount += refund_value

                # Delete item if fully refunded, otherwise save
                if sale_item.qty == 0:
                    sale_item.delete()
                else:
                    sale_item.save()

                # Restock inventory
                inventory = product.inventory
                inventory.qty += qty_to_refund
                inventory.save()

            # Update sale total amount
            sale.total_amount -= total_refund_amount
            sale.save()

        # Return success response with refund details
        return Response({
            "message": "Refund processed successfully",
            "refund_amount": float(total_refund_amount),
            "new_total": float(sale.total_amount)
        }, status=status.HTTP_200_OK)