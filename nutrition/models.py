from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.recipe.name} → {self.ingredient.name} ({self.quantity}g)"
