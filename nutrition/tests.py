from django.test import TestCase, Client
from django.contrib.auth.models import User
from nutrition.models import Ingredient, Recipe, RecipeIngredient


class APITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.force_login(self.user)

    def test_create_ingredient(self):
        response = self.client.post("/api/ingredients", {
            "name": "Курица",
            "calories": 165,
            "protein": 31,
            "fat": 3.6,
            "carbs": 0
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Ingredient.objects.filter(name="Курица").exists())

    def test_create_recipe(self):
        self.client.post("/api/ingredients", {
            "name": "Рис",
            "calories": 130,
            "protein": 2.7,
            "fat": 0.3,
            "carbs": 28
        }, content_type="application/json")

        ingredient_id = Ingredient.objects.get(name="Рис").id

        response = self.client.post("/api/recipes", {
            "name": "Рис с курицей",
            "ingredients": [
                {"ingredient_id": ingredient_id, "quantity": 200}
            ]
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recipe.objects.filter(name="Рис с курицей").exists())

    def test_recipe_result(self):
        self.client.post("/api/ingredients", {
            "name": "Яйцо",
            "calories": 155,
            "protein": 13,
            "fat": 11,
            "carbs": 1.1
        }, content_type="application/json")
        ing = Ingredient.objects.get(name="Яйцо")

        self.client.post("/api/recipes", {
            "name": "Омлет",
            "ingredients": [{"ingredient_id": ing.id, "quantity": 100}]
        }, content_type="application/json")
        recipe_id = Recipe.objects.get(name="Омлет").id

        result = self.client.get(f"/api/recipes/{recipe_id}")
        self.assertEqual(result.status_code, 200)
        data = result.json()
        self.assertEqual(data["total_calories"], 155)
        self.assertEqual(data["total_protein"], 13)
        self.assertEqual(data["total_fat"], 11)
        self.assertEqual(data["total_carbs"], 1.1)

    def test_logout(self):
        response = self.client.post("/auth/logout")
        self.assertEqual(response.status_code, 200)

        
        response = self.client.get("/api/ingredients")
        self.assertEqual(response.status_code, 401)

    def test_restrict_access_to_foreign_recipe(self):
        
        self.client.post("/api/ingredients", {
            "name": "Сыр",
            "calories": 300,
            "protein": 20,
            "fat": 25,
            "carbs": 0
        }, content_type="application/json")
        ingredient = Ingredient.objects.get(name="Сыр")
        self.client.post("/api/recipes", {
            "name": "Сырники",
            "ingredients": [{"ingredient_id": ingredient.id, "quantity": 100}]
        }, content_type="application/json")
        recipe = Recipe.objects.get(name="Сырники")

       
        other_user = User.objects.create_user(username="other", password="1234")
        self.client.logout()
        self.client.force_login(other_user)

        
        response = self.client.get(f"/api/recipes/{recipe.id}")
        self.assertEqual(response.status_code, 404)

    def test_restrict_delete_foreign_ingredient(self):
        
        self.client.post("/api/ingredients", {
            "name": "Чеснок",
            "calories": 149,
            "protein": 6.4,
            "fat": 0.5,
            "carbs": 33
        }, content_type="application/json")
        ing = Ingredient.objects.get(name="Чеснок")

        
        other_user = User.objects.create_user(username="enemy", password="1234")
        self.client.logout()
        self.client.force_login(other_user)

        
        response = self.client.delete(f"/api/ingredients/{ing.id}")
        self.assertEqual(response.status_code, 404)
