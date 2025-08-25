from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import transaction
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)

class Authority(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self): 
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    authorities = models.ManyToManyField(Authority, through='RoleAuthority')
    
    def __str__(self): 
        return self.name

class RoleAuthority(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('role', 'authority')
    
    def __str__(self):
        return f"{self.role} - {self.authority}"

class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role, through='UserRole')

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user_name or self.email

    def get_roles(self):
        return self.roles.values_list('name', flat=True)

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    def get_authorities(self):
        return Authority.objects.filter(
            roleauthority__role__in=self.roles.all()
        ).distinct()

    def has_authority(self, authority_name):
        return self.get_authorities().filter(name=authority_name).exists()

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user} - {self.role}"

# Business Models
class Category(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(unique=True, max_length=255)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,  # Allows field to be optional in forms
        related_name='created_categories'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,  # Allows field to be optional in forms
        related_name='updated_categories'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # Auto-filled on creation
    updated_at = models.DateTimeField(auto_now=True, editable=False)      # Auto-filled on update

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,  # Allows field to be optional in forms
        related_name='created_products'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,  # Allows field to be optional in forms
        related_name='updated_products'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # Auto-filled on creation
    updated_at = models.DateTimeField(auto_now=True, editable=False)      # Auto-filled on update

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Inventory(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    active = models.BooleanField(default=True)
    qty = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        unique=True
    )
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_inventories'
    )
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"{self.product} - {self.qty} ({self.status})"

    def save(self, *args, **kwargs):
        if self.qty == 0:
            self.status = 'out_of_stock'
        elif self.qty < 10:
            self.status = 'low_stock'
        else:
            self.status = 'in_stock'
        super().save(*args, **kwargs)


class Sale(models.Model):
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_items')
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        return f"{self.qty} x {self.product or 'Deleted Product'} @ {self.price}"

    def save(self, *args, **kwargs):
        if not self.product:
            raise ValidationError("Product is required")
        self.price = self.product.price
        if self.qty <= 0:
            raise ValidationError("Quantity must be positive")
        self.subtotal = self.qty * self.price

        with transaction.atomic():
            if self.pk:
                old_item = SaleItem.objects.get(pk=self.pk)
                if old_item.product and old_item.qty != self.qty:
                    old_item.product.inventory.qty += old_item.qty
                    old_item.product.inventory.save()

            inv = self.product.inventory
            if inv.qty < self.qty:
                raise ValidationError(f"Not enough stock for {self.product.name}")
            inv.qty -= self.qty
            inv.save()

            super().save(*args, **kwargs)

            total = self.sale.items.aggregate(total=models.Sum('subtotal'))['total'] or 0
            Sale.objects.filter(pk=self.sale.pk).update(total_amount=total)

    def delete(self, *args, **kwargs):
        if self.product:
            inv = self.product.inventory
            inv.qty += self.qty
            inv.save()
        super().delete(*args, **kwargs)
        total = self.sale.items.aggregate(total=models.Sum('subtotal'))['total'] or 0
        Sale.objects.filter(pk=self.sale.pk).update(total_amount=total)

    

