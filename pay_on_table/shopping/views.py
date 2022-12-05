from .models import Product, Store, Basket, BasketProduct
from .serializers import ProductSerializer, CreateBasketProductSerializer, BasketSerializer\
    , UpdateBasketProductSerializer, UpdateBasketSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


class ProductFilter(filters.FilterSet):
    store = filters.ModelMultipleChoiceFilter(
        field_name='stores',
        to_field_name='id',
        queryset=Store.objects.all(),
    )

    class Meta:
        model = Product
        fields = ['type', "store"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter


@swagger_auto_schema(method='post', request_body=CreateBasketProductSerializer)
@api_view(["POST"])
def create_basket_product(request):
    data = request.data
    serializer_class = CreateBasketProductSerializer(data=data)
    serializer_class.is_valid(raise_exception=True)
    basket_id = request.session.get('basket_id')
    if basket_id is None:
        basket = Basket()
        basket.save()
        basket_id = basket.id
    basket_objects = Basket.objects.all().get(id=basket_id)
    basket_products = basket_objects.basket_products.all().\
        filter(product=serializer_class.validated_data["product"]).first()
    if basket_products is None:
        serializer_class.save(basket_id=basket_id)
    else:
        basket_products.quantity = basket_products.quantity + serializer_class.validated_data["quantity"]
        basket_products.save()
    basket = Basket.objects.get(id=basket_id)
    serializer = BasketSerializer(instance=basket)
    request.session['basket_id'] = basket_id
    response = serializer.data
    return Response(response)


@api_view(["GET"])
def get_basket(request):
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    serializer = BasketSerializer(instance=basket)
    response = serializer.data
    return Response(response)


@api_view(["DELETE"])
def delete_basket(request):
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    basket.delete()
    return Response("deleted")


@api_view(["DELETE"])
def delete_basket_product(request, pk):
    basket_product = BasketProduct.objects.all().get(id=pk)
    basket_product.delete()
    return Response("deleted")


@swagger_auto_schema(method='patch', request_body=UpdateBasketProductSerializer)
@api_view(["PATCH"])
def update_basket_product(request, pk):
    data = request.data
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    basket_product = BasketProduct.objects.all().get(id=pk)
    serializer = UpdateBasketProductSerializer(instance=basket_product, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
    serializer_final = BasketSerializer(instance=basket)
    response = serializer_final.data
    return Response(response)


@swagger_auto_schema(method='patch', request_body=UpdateBasketSerializer)
@api_view(["PATCH"])
def update_basket(request):
    data = request.data
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    serializer = UpdateBasketSerializer(instance=basket, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
    serializer_final = BasketSerializer(instance=basket)
    response = serializer_final.data
    return Response(response)
