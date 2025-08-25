from rest_framework import serializers
from polls.models import Category, Product,Sale, Inventory, SaleItem,User,Authority,Role,UserRole
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if needed, e.g. user roles
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Override to allow login with email (instead of username)
        # You may need to adjust authentication backend accordingly
        return super().validate(attrs)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'user_name', 'is_staff', 'is_active', 'roles']

    def get_roles(self, obj):
        # Return serialized role data instead of raw list
        roles = Role.objects.filter(userrole__user=obj)
        return RoleSerializer(roles, many=True).data


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    # Accept roles as a list of role names or IDs (write-only)
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'user_name', 'password', 'is_staff', 'is_active', 'roles']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)
        self._assign_roles(user, roles_data)
        return user

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('roles', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if roles_data is not None:  # Replace roles completely
            UserRole.objects.filter(user=instance).delete()
            self._assign_roles(instance, roles_data)

        return instance

    def _assign_roles(self, user, roles_data):
        for role_name in roles_data:
            try:
                role = Role.objects.get(name=role_name)
                UserRole.objects.get_or_create(user=user, role=role)
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"Role '{role_name}' does not exist")


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer()

    class Meta:
        model = UserRole
        fields = ['id', 'role']


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    updated_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Category
        fields = ['id', 'active', 'name', 'created_by', 'updated_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']  # Prevent manual input

    def validate(self, data):
        # Optional: Add custom validation if needed
        return data

class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    updated_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Product
        fields = ['id', 'active', 'description', 'name', 'price', 'category', 
                  'created_by', 'updated_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']  # Prevent manual input

    def validate(self, data):
        # Optional: Add custom validation (e.g., ensure price is positive)
        if 'price' in data and data['price'] < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return data

class InventorySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True  # Product is required for Inventory
    )
    last_updated_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)  # Optional: for display

    class Meta:
        model = Inventory
        fields = ['id', 'active', 'qty', 'status', 'product', 'product_name', 
                  'last_updated_by', 'last_updated']
        read_only_fields = ['status', 'last_updated']  # Status is auto-set, last_updated is auto-filled

    def validate(self, data):
        # Ensure qty is non-negative
        if 'qty' in data and data['qty'] < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return data


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'qty', 'price', 'subtotal']
        read_only_fields = ['price', 'subtotal', 'product_name']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer_name', 'total_amount', 'created_by', 'created_by_name', 'created_at', 'updated_at', 'items']
        read_only_fields = ['total_amount', 'created_by_name', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sale = Sale.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)
        return sale

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SaleItem.objects.create(sale=instance, **item_data)
        return instance
    
class SaleItemRefundSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    qty = serializers.IntegerField(min_value=1)
class RefundSerializer(serializers.Serializer):
    items = SaleItemRefundSerializer(many=True)

