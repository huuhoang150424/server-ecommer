from django.urls import path
from .views import *


urlpatterns = [
    path("getAllOrders",getAllOrders,name="getAllOrders"),
    path("getOrderByUser",getOrderByUser,name="getOrderByUser"),
    path("cod",createOrderCod,name="cod"),
    path("confirmOrder/<uuid:id>",confirmOrder,name="confirmOrder"),
    path("destroy/<uuid:id>",destroyOrders,name="destroy"),
    path("received/<uuid:id>",receivedOrder,name="received"),

    path("getOrderDestroy",getOrderDestroy,name="getOrderDestroy"),
    path("getOrderShipped",getOrderShipped,name="getOrderShipped"),
    path("getOrderProcessing",getOrderProcessing,name="getOrderProcessing"),
    path("getOrderReceived",getOrderReceived,name="getOrderReceived"),
    path("getOrderHistory/<uuid:id>",getOrderHistory,name="getOrderHistory"),
    path("momo",createOrderMomo,name="momo"),
]
