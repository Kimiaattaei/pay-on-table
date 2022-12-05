from rest_framework.test import APITestCase
from rest_framework import status
from shopping.models import Product, Store, Allergen


class ProductsTestCase(APITestCase):

    def test_list_of_products(self):
        data = {
            "name": "book",
            "price": 100,
            "description": "nemidonam",
            "type": "normal",
            "ingredients": "apple"
        }
        data_store = {
            "name": "dakeh",
            "lat": 1010,
            "lon": 4444,
        }
        data_allergen = {
            "name": "moghava"
        }
        store = Store(name=data_store["name"], lat=data_store["lat"], lon=data_store["lon"])
        store.save()
        allergen = Allergen(name=data_allergen["name"])
        allergen.save()
        product = Product(type=data["type"], name=data["name"], description=data["description"],
                          price=data["price"], ingredients=data["ingredients"])
        product.save()
        product.stores.add(store)
        product.save()
        product.allergen.add(allergen)
        product.save()
        response = self.client.get("", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn("name", result[0])
        self.assertIn("price", result[0])
        self.assertIn("description", result[0])
        self.assertIn("type", result[0])
        self.assertIn("ingredients", result[0])
        stores = result[0]["stores"]
        self.assertEqual(type(stores), list)
        self.assertEqual(len(stores), 1)
        allergen = result[0]["allergen"]
        self.assertIn("id", allergen[0])
        self.assertIn("name", allergen[0])


