from django.shortcuts import render
from .models import cartItemModel,cartModel
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required,user_required
from product.models import ProductModel

@api_view(['POST'])
@user_required  
def addCart(request):
    try:
        user_id = request.user.id  
        product_id = request.data.get('product_id') 
        quantity = int(request.data.get('quantity', 1)) 

        product = ProductModel.objects.get(id=product_id)
        
        if product.stock < quantity:
            return ErrorResponse({'message': 'Không đủ số lượng sản phẩm trong kho'}, status=status.HTTP_400_BAD_REQUEST)

        cart_instance, created = cartModel.objects.get_or_create(user_id=user_id)

        if created:
            cart_item = cartItemModel.objects.create(
                cart=cart_instance, 
                product_id=product_id,
                quantity=quantity
            )
            return SuccessResponse({
                'message': 'Giỏ hàng đã được tạo và sản phẩm đã được thêm thành công'
            }, status=status.HTTP_201_CREATED)
        
        cart_item, created = cartItemModel.objects.get_or_create(
            cart=cart_instance, 
            product_id=product_id
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            return SuccessResponse({
                'message': 'Sản phẩm đã được thêm vào giỏ hàng'
            }, status=status.HTTP_200_OK)

        cart_item.quantity = quantity
        cart_item.save()
        return SuccessResponse({
            'message': 'Sản phẩm đã được thêm vào giỏ hàng thành công'
        }, status=status.HTTP_201_CREATED)

    except ProductModel.DoesNotExist:
        return ErrorResponse({'message': 'Sản phẩm không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)






@api_view(['GET'])
@user_required  
def getCart(request):
    try:
        user_id = request.user.id
        cart = cartModel.objects.prefetch_related('cart_items__product').get(user_id=user_id)

        serializers = CartSerializer(cart)

        return SuccessResponse({
            'message': 'Thành công',
            'data': serializers.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['DELETE'])
@user_required  
def removeCart(request,cartItemId):
    try:
        user_id = request.user.id
        cartItem=cartItemModel.objects.get(id=cartItemId)
        cartItem.delete()
        return SuccessResponse({
            'message': 'Xóa thành công'
        },status=status.HTTP_200_OK)

    except cartItemModel.DoesNotExist:
        return ErrorResponse({'message':'sản phẩm không tồn tại trong giỏ hàng'},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@user_required  
def removeAllCart(request):
    try:
        user_id=request.user.id
        cart=cartModel.objects.get(user_id=user_id)

        cart.cart_items.all().delete()
        return SuccessResponse({
            'message': 'Xóa tất cả thành công'
        })
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@user_required  
def updateCart(request, cartItemId):
    try:
        new_quantity = int(request.data.get("quantity"))
        product_id=request.data.get("product_id")

        product = ProductModel.objects.get(id=product_id)
        print(product)
        if not new_quantity or int(new_quantity)  <= 0  or product.stock<new_quantity:
            return ErrorResponse({'message': 'Số lượng không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        cartItem = cartItemModel.objects.get(id=cartItemId)

        cartItem.quantity = new_quantity
        cartItem.save()

        return SuccessResponse({
            'message': 'Cập nhật giỏ hàng thành công'
        }, status=status.HTTP_200_OK)
    
    except cartItemModel.DoesNotExist:
        return ErrorResponse({'message': 'Sản phẩm không tồn tại trong giỏ hàng'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
