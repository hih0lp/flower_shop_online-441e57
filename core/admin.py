from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Flower, Order, OrderItem


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created')
    list_filter = ('status', 'created')
    search_fields = ('user__username', 'address', 'phone')
    inlines = [OrderItemInline]
