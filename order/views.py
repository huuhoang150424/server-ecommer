from django.shortcuts import render

from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required,user_required
from product.models import ProductModel
from .models import orderModel,orderDetailModel



@api_view(['GET'])
@user_required  
def getTotalPrice(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_required  
def getAllOrders(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@user_required  
def addOrder(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@user_required  
def confirmPayment(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@user_required  
def destroyOrders(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)