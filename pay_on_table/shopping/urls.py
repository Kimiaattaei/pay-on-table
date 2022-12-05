from .views import ProductViewSet, create_basket_product, \
    get_basket, delete_basket, delete_basket_product, update_basket_product, update_basket
from rest_framework.routers import DefaultRouter
from django.urls import path


router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')
urlpatterns1 = [
    path("create-basket-product/", create_basket_product),
    path("get-basket/", get_basket),
    path("delete-basket/", delete_basket),
    path("delete-basket-product/<int:pk>/", delete_basket_product),
    path("update-basket-product/<int:pk>/", update_basket_product),
    path("update-basket/", update_basket),
]
urlpatterns = urlpatterns1 + router.urls
