from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Role, Authority, RoleAuthority, UserRole,
    Category, Product, Inventory, Sale, SaleItem
)

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    autocomplete_fields = ['role']  # Optional for better UX if Role has many entries
    

class RoleAuthorityInline(admin.TabularInline):
    model = RoleAuthority
    extra = 1
    autocomplete_fields = ['authority']  # Optional for better UX if Authority has many entries

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'user_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'user_name')
    ordering = ('email',)
    filter_horizontal = ()  # You can add many-to-many fields here if needed

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('user_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    inlines = [UserRoleInline]

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [RoleAuthorityInline]

class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at', 'updated_at')
    list_filter = ('active',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'qty', 'status', 'last_updated')
    list_filter = ('status',)
    search_fields = ('product__name',)
    readonly_fields = ('last_updated',)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('subtotal', 'price')
    autocomplete_fields = ['product']  # Improve product selection

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name',)
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [SaleItemInline]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Authority, AuthorityAdmin)
admin.site.register(RoleAuthority)
admin.site.register(UserRole)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem)
