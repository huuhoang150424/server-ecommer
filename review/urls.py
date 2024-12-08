from django.urls import path
from .views import *


urlpatterns = [

    path("ratingProduct/<uuid:productId>",ratingProduct,name="ratingProduct"),
    path("comment/<uuid:productId>",comment,name="comment"),
    path("getCommentProduct/<uuid:productId>",getCommentProduct,name="getCommentProduct"),
    path("updateComment/<uuid:id>",updateComment,name="updateComment"),
    path("deleteComment/<uuid:id>",deleteComment,name="deleteComment"),
]
