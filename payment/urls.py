from django.urls import path
from .views import *


urlpatterns = [
    path("buyProductCod",buyProductCod,name="buyProductCod"),
    path("buyProductMomo",buyProductMomo,name="buyProductMomo"),
]
