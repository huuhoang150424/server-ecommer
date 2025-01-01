from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required
from users.models import Users
from order.models import orderModel
from review.models import RatingModel,CommentModel
from product.models import ProductModel
from django.db.models import Count,Sum
from datetime import datetime


#statistical

@api_view(['GET'])
@admin_required
def getUserBuyProductSoMuch(request):
    try:
        users = Users.objects.annotate(order_count=Count('orders')).order_by('-order_count')[:20]
        serializer = GetUserBuyProductSoMuchSerializer(users, many=True)
        return SuccessResponse({
            'message': 'Thành công',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(
            error_message=str(e), 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required
def getRevenueForTheYear(request, year):
    try:
        orders = orderModel.objects.filter(created_at__year=year)
        result = [{'name': f'T{month}', 'total': 0} for month in range(1, 13)]
        for order in orders:
            month = order.created_at.month
            result[month - 1]['total'] += order.total_amount
        return SuccessResponse({
            'message': 'Thành công',
            'data': result,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse( error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@admin_required
def getTargetForTheMonth(request):
    try:
        currentMonth=datetime.now().month
        currentYear = datetime.now().year

        user_count = Users.objects.filter(
            created_at__month=currentMonth,
            created_at__year=currentYear
        ).count()
        order_count = orderModel.objects.filter(
            created_at__month=currentMonth,
            created_at__year=currentYear
        ).count()


        comment_count = CommentModel.objects.filter(
            created_at__month=currentMonth,
            created_at__year=currentYear
        ).count()

        total_revenue = orderModel.objects.filter(
            created_at__month=currentMonth,
            created_at__year=currentYear
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return SuccessResponse({
            'message': 'Thành công',
            'data': {
                'user_count': user_count,
                'order_count': order_count,
                'comment_count': comment_count,
                'total_revenue': total_revenue
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse( error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)