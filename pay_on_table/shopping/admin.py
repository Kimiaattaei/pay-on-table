from django.contrib import admin
from .models import Store, Allergen, Product, ProductPictures, Basket, BasketProduct


class BasketProductInline(admin.TabularInline):
    model = BasketProduct


class BasketAdmin(admin.ModelAdmin):
    inlines = [
        BasketProductInline,
    ]


admin.site.register(Store)
admin.site.register(Allergen)
admin.site.register(Product)
admin.site.register(ProductPictures)
admin.site.register(Basket, BasketAdmin)
admin.site.register(BasketProduct)
