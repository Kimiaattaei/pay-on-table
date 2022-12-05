from rest_framework import serializers
from .models import Product, Allergen, BasketProduct,Basket


class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    allergen = AllergenSerializer(many=True)

    class Meta:
        model = Product
        fields = ["stores", "name", "price", "description", "allergen", "type", "ingredients"]


class CreateBasketProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketProduct
        fields = ["product", "quantity"]


class BasketProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name")
    price = serializers.FloatField(source="product.price")

    class Meta:
        model = BasketProduct
        fields = ["id", "name", "quantity", "price"]


class BasketSerializer(serializers.ModelSerializer):
    basket_products = BasketProductSerializer(many=True)

    class Meta:
        model = Basket
        fields = ["id", "note", "number", "basket_products"]


class UpdateBasketProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BasketProduct
        fields = ["quantity"]


class UpdateBasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = ["note"]
