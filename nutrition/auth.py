from ninja import Router
from pydantic import BaseModel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


auth_router = Router()

class RegisterSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

@auth_router.post("register", tags=["Аутентификация"], summary="Регистрация")
def register_user(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "Пользователь с таким именем уже существует"}

    user = User.objects.create_user(
        username=data.username,
        password=data.password
    )
    return {"success": True, "user_id": user.id}


@auth_router.post("login", tags=["Аутентификация"], summary="Войти")
def login_user(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)
    if user is not None:
        login(request, user)
        return {"success": True}
    return {"error": "Неверный логин или пароль"}

@auth_router.post("logout", tags=["Аутентификация"], summary="Выйти")
def logout_user(request):
    logout(request)
    return {"success": True}


@auth_router.get("me", tags=["Аутентификация"], summary="Вывод имени работающего на данный момент")
def get_current_user(request):
    if request.user.is_authenticated:
        return {"username": request.user.username}
    return {"error": "Вы не авторизованы"}
