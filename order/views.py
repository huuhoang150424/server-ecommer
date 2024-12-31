from django.shortcuts import render
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required,user_required
from product.models import ProductModel
from cart.models import cartModel,cartItemModel
from payment.models import PaymentMethod,PaymentModel,PaymentStatus
from .models import *
from django_redis import get_redis_connection
from django.db import transaction
from payment.models import *
from payment.locks import *
import hashlib
import json
import random
import base64
import time
from django.conf import settings
from rest_framework.response import Response
from django.core.paginator import Paginator
from utils.pagination import CustomPagination
import datetime
from django.db.models import Sum




@api_view(['POST'])
@user_required
def createOrderCod(request):
    try:
        with transaction.atomic():
            user_id = request.user.id
            cartItems = request.data.get("carts", [])
            shipping_address= request.data.get("shipping_address")
            receiver_name = request.data.get("receiver_name")
            receiver_phone= request.data.get("receiver_phone")

            if not cartItems:
                return ErrorResponse({
                    'message': 'Giỏ hàng của bạn trống.'
                }, status=status.HTTP_400_BAD_REQUEST)
            total_amount = 0
            product_locks = []

            # Kiểm tra và khóa từng sản phẩm
            for item in cartItems:
                product_id = item['product']['id']
                lock = lock_product(product_id)
                if lock is None:
                    return ErrorResponse({
                        'message': f"Sản phẩm {product_id} đang được mua bởi người khác."
                    }, status=status.HTTP_400_BAD_REQUEST)
                product_locks.append(lock)

                try:
                    cart_item_instance = cartItemModel.objects.get(id=item['id'])
                except cartItemModel.DoesNotExist:
                    return ErrorResponse({
                        'message': f'Cart item với ID {item["id"]} không tồn tại hoặc không thuộc về bạn.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                product_instance = cart_item_instance.product
                print(product_instance)
                if (product_instance.stock<cart_item_instance.quantity):
                    return ErrorResponse({"error": f"Sản phẩm {product_instance.product_name} không đủ số lượng."}, status=status.HTTP_400_BAD_REQUEST)

                product_instance.stock-=cart_item_instance.quantity
                product_instance.save()
                total_amount += cart_item_instance.quantity * item['product']['price']

            order = orderModel.objects.create(
                user=request.user,
                total_amount=total_amount,
                status=statusOrderModel.NOT_CONFIRMED,
                shipping_address=shipping_address,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone
            )
            orderHistoryModel.objects.create(
                status=StatusModel.PROCESSING,
                order=order,
                change_by=request.user
            )
            for item in cartItems:
                cart_item_instance = cartItemModel.objects.get(id=item['id'])
                orderDetailModel.objects.create(
                    order=order,
                    product=cart_item_instance.product,
                    price=item['product']['price']*item['quantity'],
                    quantity=item['quantity']
                )
                cart_item_instance.delete()
            PaymentModel.objects.create(
                order=order,
                payment_method=PaymentMethod.COD,
                payment_status=PaymentStatus.PENDING,
                transaction_id='N/A'
            )
            # Giải phóng khóa sau khi tất cả các thao tác hoàn thành
            for lock in product_locks:
                if lock.locked():  # Kiểm tra xem khóa có đang được nắm giữ trước khi giải phóng
                    lock.release()

            return SuccessResponse({
                'message': 'Tạo đơn hàng và thanh toán COD thành công',
                'order_id': order.id
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        for lock in product_locks:
            if lock.locked():
                lock.release()
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def momo_notify(request):
    try:
        # Lấy dữ liệu trả về từ MoMo
        data = request.data

        # Kiểm tra chữ ký bảo mật
        raw_signature = f"partnerCode={data['partnerCode']}&accessKey={data['accessKey']}&requestId={data['requestId']}&amount={data['amount']}&orderId={data['orderId']}&orderInfo={data['orderInfo']}&transId={data['transId']}&resultCode={data['resultCode']}"
        signature = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest().upper()

        if signature != data['signature']:
            return Response({'message': 'Chữ ký không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        if data['resultCode'] == '0':  # Thanh toán thành công
            # Cập nhật trạng thái thanh toán trong cơ sở dữ liệu
            order = orderModel.objects.get(id=data['orderId'])
            order.payment_status = PaymentStatus.COMPLETED
            order.save()

            return Response({'message': 'Thanh toán thành công'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Thanh toán thất bại'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'message': f'Lỗi: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_momo_payment(order_id, amount):
    partner_code = settings.MOMO_PARTNER_CODE
    access_key = settings.MOMO_ACCESS_KEY
    secret_key = settings.MOMO_SECRET_KEY
    order_info = settings.MOMO_ORDER_INFO
    return_url = "http://yourdomain.com/return_url"  # URL trả về sau khi thanh toán thành công
    notify_url = "http://yourdomain.com/notify_url"  # URL MoMo sẽ gọi sau khi thanh toán

    # Tạo dữ liệu yêu cầu thanh toán
    order_data = {
        'partnerCode': partner_code,
        'accessKey': access_key,
        'requestId': str(random.randint(100000, 999999)),
        'amount': amount,
        'orderId': order_id,
        'orderInfo': order_info,
        'returnUrl': return_url,
        'notifyUrl': notify_url,
        'extraData': '',  # Dữ liệu bổ sung, có thể để trống
    }

    # Tạo chữ ký bảo mật
    raw_signature = f"partnerCode={partner_code}&accessKey={access_key}&requestId={order_data['requestId']}&amount={amount}&orderId={order_id}&orderInfo={order_info}&returnUrl={return_url}&notifyUrl={notify_url}&extraData={order_data['extraData']}"
    signature = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest().upper()
    
    order_data['signature'] = signature

    # Gửi yêu cầu thanh toán đến MoMo API
    response = requests.post(settings.MOMO_API_URL, data=order_data)
    return response.json()

@api_view(['POST'])
def createOrderMomo(request):
    order_id = request.data.get("order_id")
    amount = request.data.get("amount")

    if not order_id or not amount:
        return Response({"message": "Thiếu thông tin đơn hàng hoặc số tiền."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Tạo yêu cầu thanh toán MoMo
        response = create_momo_payment(order_id, amount)

        if response['resultCode'] == '0':  # Thanh toán thành công
            return Response({
                'message': 'Tạo yêu cầu thanh toán MoMo thành công',
                'payUrl': response['payUrl']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Có lỗi xảy ra khi tạo yêu cầu thanh toán MoMo',
                'error_message': response.get('message', 'Không rõ lỗi')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"message": f"Lỗi hệ thống: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@admin_required
def getAllOrders(request):
    try:
        orders = orderModel.objects.all()
        paginator = CustomPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)

        if paginated_orders is None:  
            orders_serializer = OrderSerializer(orders, many=True)
            return SuccessResponse({
                'totalItems': len(orders),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(orders),
                'data': orders_serializer.data
            }, status=status.HTTP_200_OK)
        orders_serializer = OrderSerializer(paginated_orders, many=True)
        return paginator.get_pagination_response(orders_serializer.data)
    except Exception as e:
        return ErrorResponse({
            'error_message': f"Lỗi : {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required
def getOrderByUser(request):
    try:
        user=request.user
        orders = orderModel.objects.filter(user=user)
        orders_serializer=OrderByUserSerializer(orders, many=True)

        return SuccessResponse({
            'data': orders_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse({
            'error_message': f"Lỗi : {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






@api_view(['POST'])
@user_required  
def createOrderMomo(request):
    try:

        return SuccessResponse({
            'message': 'Thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@user_required
def findOrder(request, id):
    try:
        user = request.user
        order = orderModel.objects.filter(id=id, user=user).first()

        return SuccessResponse({"message": "Thành công"},status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#handle order history
@api_view(['POST'])
@user_required
def destroyOrders(request, id):
    try:
        user = request.user
        order = orderModel.objects.filter(id=id, user=user).first()
        if not order:
            return ErrorResponse(
                {"error_message": "Đơn hàng không tồn tại hoặc bạn không có quyền hủy đơn này."},
                status=status.HTTP_404_NOT_FOUND
            )
        if order.status == statusOrderModel.CONFIRMED:
            return ErrorResponse(
                {"error_message": "Đơn hàng đã được xác nhận, không thể hủy."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status == statusOrderModel.NOT_CONFIRMED and order.order_histories.filter(status=StatusModel.CANCELLED).exists():
            return ErrorResponse(
                {"error_message": "Đơn hàng đã bị hủy trước đó."},
                status=status.HTTP_400_BAD_REQUEST
            )
        currentHistory = orderHistoryModel.objects.filter(
            order=order,
            changed_at__isnull=False,
            status__in=[StatusModel.PROCESSING],
        ).order_by("-changed_at").first()
        if currentHistory:
            currentHistory.end_time = datetime.datetime.now()  
            currentHistory.save()

        orderHistoryModel.objects.create(
            status=StatusModel.CANCELLED,
            order=order,
            change_by=user
        )
        return SuccessResponse({"message": "Hủy đơn hàng thành công"},status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@admin_required
def confirmOrder(request, id):
    try:
        order = orderModel.objects.get(id=id)
        if order.status != statusOrderModel.NOT_CONFIRMED:
            return ErrorResponse(
                {"error_message": "Đơn hàng không thể xác nhận."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.order_histories.filter(status=StatusModel.CANCELLED).exists():
            return ErrorResponse(
                {"error_message": "Đơn hàng đã bị hủy không thể xác nhận."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = statusOrderModel.CONFIRMED
        order.save()
        currentHistory = orderHistoryModel.objects.filter(
            order=order,
            changed_at__isnull=False,
            status__in=[StatusModel.PROCESSING],
        ).order_by("-changed_at").first()
        if currentHistory:
            currentHistory.end_time = datetime.datetime.now()  
            currentHistory.save()
        orderHistoryModel.objects.create(
            status=StatusModel.SHIPPED,
            order=order,
            change_by=request.user
        )
        return SuccessResponse(
            {"message": "Xác nhận đơn hàng thành công."},
            status=status.HTTP_200_OK
        )
    except orderModel.DoesNotExist:
        return ErrorResponse(error_message="Đơn hàng không tồn tại.",status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message= str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@user_required
def receivedOrder(request, id):
    try:
        user = request.user
        order = orderModel.objects.filter(id=id, user=user).first()
        if not order:
            return ErrorResponse(
                {"error_message": "Đơn hàng không tồn tại hoặc bạn không có quyền xác nhận đơn này."},
                status=status.HTTP_404_NOT_FOUND
            )
        if order.status == statusOrderModel.NOT_CONFIRMED:
            return ErrorResponse(
                {"error_message": "Đơn hàng chưa được xác nhận."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not order.order_histories.filter(status=StatusModel.SHIPPED).exists():
            return ErrorResponse(
                {"error_message": "Đơn hàng chưa được giao."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.order_histories.filter(status=StatusModel.RECEIVED).exists():
            return ErrorResponse(
                {"error_message": "Đơn hàng đã được xác nhận là 'Đã nhận hàng' trước đó."},
                status=status.HTTP_400_BAD_REQUEST
            )
        currentHistory = orderHistoryModel.objects.filter(
            order=order,
            changed_at__isnull=False,
            status__in=[StatusModel.SHIPPED],
        ).order_by("-changed_at").first()
        
        if currentHistory:
            currentHistory.end_time = datetime.datetime.now()  
            currentHistory.save()
        orderHistoryModel.objects.create(
            status=StatusModel.RECEIVED,
            order=order,
            change_by=user
        )
        return SuccessResponse(
            {"message": "Xác nhận đã nhận hàng thành công."},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(
            {"error_message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



#get orderhistory
@api_view(['GET'])
@user_required
def getOrderDestroy(request):
    try:
        user = request.user
        cancelled_orders = orderHistoryModel.objects.filter(
            order__user=user,
            status=StatusModel.CANCELLED,
            end_time__isnull=True
        ).select_related('order')

        serializer = OrderHistoryByUserSerializer(cancelled_orders, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(
            error_message=str(e), 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@user_required
def getOrderShipped(request):
    try:
        user = request.user
        cancelled_orders = orderHistoryModel.objects.filter(
            order__user=user,
            status=StatusModel.SHIPPED,
            end_time__isnull=True
        ).select_related('order')

        serializer = OrderHistoryByUserSerializer(cancelled_orders, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_required
def getOrderProcessing(request):
    try:
        user = request.user
        cancelled_orders = orderHistoryModel.objects.filter(
            order__user=user,
            status=StatusModel.PROCESSING,
            end_time__isnull=True
        ).select_related('order')

        serializer = OrderHistoryByUserSerializer(cancelled_orders, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return ErrorResponse(error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_required
def getOrderReceived(request):
    try:
        user = request.user
        cancelled_orders = orderHistoryModel.objects.filter(
            order__user=user,
            status=StatusModel.RECEIVED,
            end_time__isnull=True
        ).select_related('order')

        serializer = OrderHistoryByUserSerializer(cancelled_orders, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_required
def getOrderHistory(request, id):
    try:
        user = request.user
        order = orderModel.objects.filter(
            id=id,
            user=user
        ).prefetch_related('order_histories__change_by').first()

        if not order:
            return ErrorResponse(
                {"error_message": "Hóa đơn không tồn tại hoặc bạn không có quyền truy cập."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderHistorySerializer(order)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(
            error_message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#statistical

@api_view(['GET'])
@admin_required
def getRevenueForTheYear(request, year):
    try:
        orders = orderModel.objects.filter(created_at__year=year)
        result = [{'name': f'T{month}', 'total_revenue': 0} for month in range(1, 13)]
        for order in orders:
            month = order.created_at.month
            result[month - 1]['total_revenue'] += order.total_amount
        return SuccessResponse({
            'message': 'Thành công',
            'data': result,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse( error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)