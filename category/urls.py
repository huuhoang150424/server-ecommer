from .views import *
from django.urls import path

urlpatterns = [
    path("createCat",createCat,name="createCat"),
    path("getCat/<uuid:catId>",getCat,name="getCat"),
    path("getAllCat",getAllCat,name="getAllCat"),
    path("updateCat/<uuid:catId>",updateCat,name="updateCat"),
    path("deleteCat/<uuid:catId>",deleteCat,name="deleteCat"),
    path("getAllClient",getAllClient,name="getAllClient"),
]
