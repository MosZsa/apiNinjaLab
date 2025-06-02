"""
URL configuration for apininjaLab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from nutrition.api import router as nutrition_router
from nutrition.auth import auth_router

api = NinjaAPI(
    title="Калькулятор калорийности блюд",
    description=(
        "API-сервис для расчёта калорийности и пищевой ценности рецептов с учётом пользовательского доступа."
        "Позволяет добавлять ингредиенты, собирать рецепты"
        "и рассчитывать итоговые БЖУ. Поддерживает регистрацию, авторизацию и работу "
        "с собственными данными пользователя."
    ),
    version="1.0.0",
    csrf=False
)

api.add_router("/api/", nutrition_router)
api.add_router("/auth/", auth_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api.urls),
]

