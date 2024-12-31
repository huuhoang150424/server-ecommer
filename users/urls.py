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
    path("getUser",getUser,name="getUser"),
    path("changePassword",changePassword,name="changePassword"),
    path("updateProfile",updateProfile,name="updateProfile"),
    path("changePhone",changePhone,name="changePhone"),
    path("resetPassword",resetPassword,name="resetPassword"),
    path("deleteUser/<uuid:id>",deleteUser,name="deleteUser"),
    path("updateUser/<uuid:id>",updateUser,name="updateUser"),
    path("addAddress",addAddress,name="addAddress"),
    path("deleteAddress",deleteAddress,name="deleteAddress"),

    #statistical
    path("statisticalUser",getUserBuyProductSoMuch,name="statisticalUser"),
]
