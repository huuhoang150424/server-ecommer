from django.urls import path
from .views import register,login,refreshToken,logout,loginWithGoogle


# define routing
urlpatterns = [
    path("register",register,name="register"),
    path("login",login,name="login"),
    path("refresh-token",refreshToken,name="refresh-token"),
    path("logout",logout,name="logout"),
    path("loginWithGoogle",loginWithGoogle,name="loginWithGoogle"),
]
