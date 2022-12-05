from django.conf import settings
from django.db import models
from hashids import Hashids
import uuid


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return f'{self.name}  {self.id}'


class Allergen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    NORMAL = "normal"
    TYPE_CHOICES = [
        (VEGAN, 'vegan'),
        (VEGETARIAN, 'vegetarian'),
        (NORMAL, 'normal'),
    ]
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=NORMAL,
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stores = models.ManyToManyField(to=Store)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.FloatField()
    allergen = models.ManyToManyField(to=Allergen, blank=True)
    ingredients = models.TextField()

    def __str__(self):
        return f'{self.name}'


class ProductPictures(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pic = models.ImageField()
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product.name}  {self.id}'


class Basket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(null=True, blank=True)
    in_progress = "in progress"
    waiting_for_payment = "waiting for payment"
    paid = "paid"
    STATUS_CHOICES = [
        (in_progress, 'in progress'),
        (waiting_for_payment, 'waiting for payment'),
        (paid, 'paid'),
    ]
    status = models.CharField(
        max_length=60,
        choices=STATUS_CHOICES,
        default=in_progress,
    )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.number is None:
            hashids = Hashids(min_length=settings.MIN_LENGTH_HASHIDS, alphabet=settings.ALPHABET_HASHIDS,
                              salt=settings.SALT_HASHIDS)
            self.number = hashids.encode(self.id)
            super().save()

    def __str__(self):
        return f'{self.id}'


class BasketProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    basket = models.ForeignKey(to=Basket, on_delete=models.CASCADE, related_name="basket_products")
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.product.name}  {self.basket.id}'
