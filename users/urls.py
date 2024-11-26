from django.urls import path
from .views import *


# define routing
urlpatterns = [
    path("register",register,name="register"),
    path("login",login,name="login"),
    path("refresh-token",refreshToken,name="refresh-token"),
    path("logout",logout,name="logout"),
    path("loginWithGoogle",loginWithGoogle,name="loginWithGoogle"),
    path("verifyCode",verifyCode,name="verifyCode"),
    path("forgotPassword",forgotPassword,name="forgotPassword"),
    path("getAllUser",getAllUser,name="getAllUser"),
    path("createUser",createUser,name="createUser"),
    path("getUser/<uuid:id>",getUser,name="getUser"),
    path("changePassword/<uuid:id>",changePassword,name="changePassword"),
    path("resetPassword",resetPassword,name="resetPassword"),
    path("deleteUser/<uuid:id>",deleteUser,name="deleteUser"),
    path("updateUser/<uuid:id>",updateUser,name="updateUser"),
]
