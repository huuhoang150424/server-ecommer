from django.urls import path
from .views import *


urlpatterns = [
    #statistical
    path("statisticalUser",getUserBuyProductSoMuch,name="statisticalUser"),
    path("getRevenueForTheYear/<int:year>", getRevenueForTheYear, name="getRevenueForTheYear"),
    path("getTargetForTheMonth", getTargetForTheMonth, name="getTargetForTheMonth")
]
