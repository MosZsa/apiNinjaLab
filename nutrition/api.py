from ninja import Router
from typing import List
from pydantic import BaseModel
from django.shortcuts import get_object_or_404
from nutrition.models import Ingredient, Recipe, RecipeIngredient
from nutrition.session_auth import SessionAuth

router = Router(auth=SessionAuth())

class IngredientIn(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

class IngredientOut(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

    class Config:
        from_attributes = True

class RecipeIngredientIn(BaseModel):
    ingredient_id: int
    quantity: float

class RecipeIn(BaseModel):
    name: str
    ingredients: List[RecipeIngredientIn]

class RecipeOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class RecipeResult(BaseModel):
    id: int
    name: str
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float


@router.post("/ingredients", response=IngredientOut, tags=["Ингредиенты"], summary="Создать ингредиент")
def create_ingredient(request, data: IngredientIn):
    obj = Ingredient.objects.create(user=request.user, **data.dict())
    return IngredientOut.from_orm(obj)

@router.get("/ingredients", response=List[IngredientOut], tags=["Ингредиенты"], summary="Получить список ингредиентов")
def list_ingredients(request, search: str = None):
    qs = Ingredient.objects.filter(user=request.user)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs

@router.get("/ingredients/{ingredient_id}", response=IngredientOut, tags=["Ингредиенты"], summary="Получить ингредиент по ID")
def get_ingredient(request, ingredient_id: int):
    obj = get_object_or_404(Ingredient, id=ingredient_id, user=request.user)
    return IngredientOut.from_orm(obj)

@router.put("/ingredients/{ingredient_id}", response=IngredientOut, tags=["Ингредиенты"], summary="Обновить ингредиент")
def update_ingredient(request, ingredient_id: int, data: IngredientIn):
    obj = get_object_or_404(Ingredient, id=ingredient_id, user=request.user)
    for field, value in data.dict().items():
        setattr(obj, field, value)
    obj.save()
    return IngredientOut.from_orm(obj)


@router.delete("/ingredients/{ingredient_id}", tags=["Ингредиенты"], summary="Удалить ингредиент")
def delete_ingredient(request, ingredient_id: int):
    obj = get_object_or_404(Ingredient, id=ingredient_id, user=request.user)
    obj.delete()
    return {"message": "Ингредиент удалён"}


@router.post("/recipes", response=RecipeOut, tags=["Рецепты"], summary="Создать рецепт")
def create_recipe(request, data: RecipeIn):
    recipe = Recipe.objects.create(user=request.user, name=data.name)
    for item in data.ingredients:
        ing = get_object_or_404(Ingredient, id=item.ingredient_id, user=request.user)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=item.quantity)
    return RecipeOut.from_orm(recipe)

@router.get("/recipes", response=List[RecipeOut], tags=["Рецепты"], summary="Получить список рецептов")
def list_recipes(
    request,
    name: str = None,
    min_calories: float = None,
    order_by: str = None,
):
    qs = Recipe.objects.filter(user=request.user)
    if name:
        qs = qs.filter(name__icontains=name)

    result = []
    for recipe in qs:
        total = 0
        for item in recipe.ingredients.all():
            factor = item.quantity / 100
            total += item.ingredient.calories * factor

        result.append({
            "recipe": recipe,
            "total_calories": round(total, 2)
        })

    if min_calories is not None:
        result = [r for r in result if r["total_calories"] >= min_calories]

    if order_by == "calories":
        result.sort(key=lambda r: r["total_calories"])
    elif order_by == "-calories":
        result.sort(key=lambda r: -r["total_calories"])

    return [r["recipe"] for r in result]

@router.get("/recipes/{recipe_id}", response=RecipeResult, tags=["Рецепты"], summary="Получить данные о рецепте")
def get_recipe_result(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    for item in recipe.ingredients.all():
        factor = item.quantity / 100
        total_calories += item.ingredient.calories * factor
        total_protein += item.ingredient.protein * factor
        total_fat += item.ingredient.fat * factor
        total_carbs += item.ingredient.carbs * factor

    return RecipeResult(
        id=recipe.id,
        name=recipe.name,
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_fat=round(total_fat, 2),
        total_carbs=round(total_carbs, 2),
    )
@router.put("/recipes/{recipe_id}", response=RecipeOut, tags=["Рецепты"], summary="Обновить рецепт")
def update_recipe(request, recipe_id: int, data: RecipeIn):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    recipe.name = data.name
    recipe.save()
    recipe.ingredients.all().delete()
    for item in data.ingredients:
        ing = get_object_or_404(Ingredient, id=item.ingredient_id, user=request.user)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=item.quantity)
    return RecipeOut.from_orm(recipe)


@router.delete("/recipes/{recipe_id}", tags=["Рецепты"], summary="Удалить рецепт")
def delete_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    recipe.delete()
    return {"message": "Рецепт удалён"}
