from django.shortcuts import render
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required,user_required
from product.models import ProductModel,StatusChoices
from order.models import orderModel,orderDetailModel
from .models import PaymentModel
from django_redis import get_redis_connection
from django.db import transaction
from django.shortcuts import get_object_or_404
import hashlib
import hmac
import json
from django.conf import settings
from .locks import *


@api_view(['POST'])
@user_required 
def buyProductCod(request):
    try:
        user = request.user
        products = request.data.get('products', []) 
        if not products:
            return ErrorResponse(error_message="Không có sản phẩm trong đơn hàng.", status=status.HTTP_400_BAD_REQUEST)

        total_amount = 0
        order_data = {}

        for product_info in products:
            product_id = product_info['product_id']
            quantity = product_info['quantity']
            product = ProductModel.objects.get(id=product_id)
            if product.stock < quantity:
                return ErrorResponse({"error": f"Sản phẩm {product.product_name} không đủ số lượng."}, status=status.HTTP_400_BAD_REQUEST)
            if product.status == StatusChoices.OUT_OF_STOCK:
                return ErrorResponse({"error": f"Sản phẩm {product.product_name} hết hàng."}, status=status.HTTP_400_BAD_REQUEST)
            if product.status == StatusChoices.DISCONTINUED:
                return ErrorResponse({"error": f"Sản phẩm {product.product_name} ngừng bán."}, status=status.HTTP_400_BAD_REQUEST)

            total_amount += product.price * quantity

        order = orderModel.objects.create(user=user, total_amount=total_amount)
        order_data['order_id'] = order.id 
        print(products)
        # Thực hiện các bước xử lý đơn hàng
        for product_info in products:
            product_id = product_info['product_id']
            quantity = product_info['quantity']
            product = ProductModel.objects.get(id=product_id)

            # Khóa sản phẩm để tránh việc tranh chấp khi đặt mua
            lock = lock_product(product.id)
            if lock.acquire(blocking=False):
                try:
                    # Thêm chi tiết đơn hàng
                    orderDetailModel.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=quantity
                    )

                    # Giảm số lượng kho và cập nhật trạng thái sản phẩm nếu hết hàng
                    product.stock -= quantity
                    if product.stock < 1:
                        product.status = StatusChoices.OUT_OF_STOCK
                    product.save()
                finally:
                    lock.release()  # Giải phóng khóa sản phẩm

        # Cập nhật tổng giá trị đơn hàng
        order.save()

        # Thêm đơn hàng vào hàng đợi Redis để xử lý sau
        add_order_to_queue(order_data)
        return SuccessResponse({"message": "Đặt hàng thành công", "order_id": order.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(e)
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



MOMO_PARTNER_CODE = 'MOMO_TEST123456'
MOMO_ACCESS_KEY = 'F8BBA842ECF85'
MOMO_SECRET_KEY = 'K951B6PE1waDMi640xX08PD3vg6EkVlz'
MOMO_ENDPOINT = 'https://test-payment.momo.vn/v2/gateway/api/create'

@api_view(['POST'])
@user_required  
def buyProductMomo(request):
    try:
        
        return SuccessResponse({
            'message': 'Đặt hàng thành công'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
