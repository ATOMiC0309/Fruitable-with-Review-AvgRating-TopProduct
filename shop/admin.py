from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Product, Email


# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'is_sale', 'quantity', 'category', 'get_image')
    list_display_links = ('name',)
    list_editable = ('price', 'quantity', 'category', 'is_sale')
    list_filter = ('category',)
    search_fields = ('name', 'description')

    def get_image(self, product):
        if product.image:
            return mark_safe(f'<img src="{product.image.url}" width="75px" style="border-radius: 15px;">')
        else:
            return 'Image not found'

    get_image.short_description = 'Rasmi'

    prepopulated_fields = {'slug': ('name', 'quantity')}


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email')
