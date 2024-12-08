from django.urls import path
from .views import *


urlpatterns = [

    path("createProduct",createProduct,name="createProduct"),
    path("editProduct/<uuid:id>",editProduct,name="editProduct"),
    path("getAllProduct",getAllProducts,name="getAllProducts"),
    path("getProductRecent",getProductRecent,name="getProductRecent"),
    path("getProduct/<slug:slug>",getProduct,name="getProduct"),
    path("getProductClient/<uuid:id>",getProductClient,name="getProductClient"),
    path("deleteProduct/<uuid:id>",deleteProduct,name="deleteProduct"),
    path("createAttribute",createAttribute,name="createAttribute"),
    path("getAllAttribute",getAllAttribute,name="getAllAttribute"),
    path("deleteAttribute/<uuid:id>",deleteAttribute,name="deleteAttribute"),
    path("updateAttribute/<uuid:id>",updateAttribute,name="updateAttribute"),

    #favorite product
    path("addFavoriteProduct",addFavoriteProduct,name="addFavoriteProduct"),
    path("removeFavoriteProduct",removeFavoriteProduct,name="removeFavoriteProduct"),
    path("getAllFavoriteProduct",getAllFavoriteProduct,name="getAllFavoriteProduct"),
]
