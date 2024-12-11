from django.urls import path
from .views import *


urlpatterns = [
    
    path("addCart",addCart,name="addCart"),
    path("getCart",getCart,name="getCart"),
    path("removeCart/<uuid:cartItemId>",removeCart,name="removeCart"),
    path("updateCart/<uuid:cartItemId>",updateCart,name="updateCart"),
    path("removeAllCart",removeAllCart,name="removeAllCart"),
]
