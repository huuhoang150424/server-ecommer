from django.urls import path
from .views import *


urlpatterns = [
    path("getAllOrders",getAllOrders,name="getAllOrders"),
    path("getOrderByUser",getOrderByUser,name="getOrderByUser"),
    path("cod",createOrderCod,name="cod"),
    path("momo",createOrderMomo,name="momo"),
    path("confirmPayment",confirmPayment,name="confirmPayment"),
    path("destroyOrders",destroyOrders,name="destroyOrders"),
    path("getAllOrdersHistory",getAllOrdersHistory,name="getAllOrdersHistory"),
]
