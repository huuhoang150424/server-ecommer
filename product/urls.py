from django.urls import path
from .views import *


urlpatterns = [

    path("createProduct",createProduct,name="createProduct"),
    path("editProduct/<uuid:id>",editProduct,name="editProduct"),
    path("getAllProduct",getAllProducts,name="getAllProducts"),
    path("getProduct/<slug:slug>",getProduct,name="getProduct"),
    path("deleteProduct/<uuid:id>",deleteProduct,name="deleteProduct"),
    path("createAttribute",createAttribute,name="createAttribute"),
    path("getAllAttribute",getAllAttribute,name="getAllAttribute"),
    path("deleteAttribute/<uuid:id>",deleteAttribute,name="deleteAttribute"),
    path("updateAttribute/<uuid:id>",updateAttribute,name="updateAttribute"),
]
