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
from zeep import Client
from rest_framework.permissions import IsAuthenticated


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
        basket_id = str(basket.id)
    basket_objects = Basket.objects.all().get(id=str(basket_id))
    basket_products = basket_objects.basket_products.all().\
        filter(product=serializer_class.validated_data["product"]).first()
    if basket_products is None:
        serializer_class.save(basket_id=str(basket_id))
    else:
        basket_products.quantity = basket_products.quantity + serializer_class.validated_data["quantity"]
        basket_products.save()
    basket = Basket.objects.get(id=str(basket_id))
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
    response.update({"price": basket.price})
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


errors = {
    100: "Operation was successful.",
    101: "successful but Verification have already been done.",
    -1: "Information submitted is incomplete.",
    -2: "Merchant ID or Acceptor IP is not correct.",
    -3: "Amount should be above 100 Toman.",
    -4: "Approved level of Acceptor is Lower than the silver.",
    -11: "Request Not found.",
    -21: "Financial operations for this transaction was not found.",
    -22: "Transaction is unsuccessful.",
    -33: "Transaction amount does not match the amount paid.",
    -34: "Limit the number of transactions or number has crossed the divide",
    -40: "There is no access to the method.",
    -41: "Additional Data related to information submitted is invalid",
    -54: "Request archived.",
}


@api_view(["GET"])
def checkout(request):
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    client = Client("https://sandbox.zarinpal.com/pg/services/WebGate/wsdl")
    if basket.status == Basket.paid:
        response = errors[101]
    else:
        pay = client.service.PaymentRequest("181a955d-7bed-4b30-bc7b-202f52ee5072", basket.price, "kimia", "pay@gmail.com",
                                            "09123456789", "http://127.0.0.1:8000/verify-payment/")
        transaction = Transaction(basket=basket, price=basket.price, reference=pay["Authority"])
        transaction.save()
        basket.status = Basket.waiting_for_payment
        basket.save()
        response = {"url": "https://sandbox.zarinpal.com/pg/StartPay/"+pay["Authority"]}
    return Response(response)


@api_view(["GET", "POST"])
def verify(request):
    basket_id = request.session.get('basket_id')
    basket = Basket.objects.all().get(id=basket_id)
    authority = request.GET.get("Authority")
    status = request.GET.get("Status")
    transaction = Transaction.objects.all().get(reference=authority)
    client = Client("https://sandbox.zarinpal.com/pg/services/WebGate/wsdl")
    if basket.status == Basket.paid:
        response = errors[101]
    else:
        verify = client.service.PaymentVerification("181a955d-7bed-4b30-bc7b-202f52ee5072", transaction.reference,
                                                    transaction.price)

        if status == 'OK':
            transaction.status = Transaction.success
            transaction.save()
            basket.status = Basket.paid
            basket.save()
        elif status == 'NOK':
            transaction.status = Transaction.failed
            transaction.save()

        if verify["Status"] == 100:
            response = verify.RefID
        else:
            response = errors[verify["Status"]]

    return Response(response)


class OrderFilter(filters.FilterSet):
    store = filters.ModelMultipleChoiceFilter(
        field_name='orders',
        to_field_name='id',
        queryset=Basket.objects.all(),
    )

    class Meta:
        model = Basket
        fields = ['id']


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Basket.objects.all().filter(status=Basket.paid)
    serializer_class = BasketSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OrderFilter

