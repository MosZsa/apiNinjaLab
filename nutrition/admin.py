from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "calories", "protein", "fat", "carbs")
    search_fields = ("name",)
    list_filter = ("user",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    inlines = [RecipeIngredientInline]
    search_fields = ("name",)
    list_filter = ("user",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "quantity")
    list_filter = ("recipe",)
