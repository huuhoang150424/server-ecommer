from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from users.decorator import admin_required,user_required
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from django.core.paginator import Paginator
from utils.pagination import CustomPagination
from .models import  RatingModel,CommentModel
from django.shortcuts import get_object_or_404


@api_view(['POST'])
def ratingProduct(request, productId):
    try:
        product = get_object_or_404(ProductModel, id=productId)
        user = request.user
        data = {
            'rating': request.data.get('rating'),
            'product': product.id,
            'user': user.id
        }
        serializer = RatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({
                'message': 'Đánh giá thành công'
            }, status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def comment(request, productId):
    try:
        product = get_object_or_404(ProductModel, id=productId)
        user = request.user
        data = {
            'comment': request.data.get('comment'),
            'product': product.id,
            'user': user.id
        }
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({
                'message': 'Bình luận thành công thành công'
            },status=status.HTTP_201_CREATED)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getCommentProduct(request, productId):
    try:
        comments = CommentModel.objects.filter(product=productId).select_related('user')

        serializer = getCommentSerializer(comments,many=True)
        return SuccessResponse({
            'data': serializer.data,
            'message': 'Thành công'
        },status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def updateComment(request, id):
    try:
        comment = CommentModel.objects.get(id=id)

        serializer = getCommentSerializer(
            instance=comment,
            data=request.data,
            context={'id':id}
        )
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({
                'data': serializer.data,
                'message': 'Cập nhật thành công'
            },status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def deleteComment(request, id):
    try:
        comment = CommentModel.objects.get(id=id)
        comment.delete()
        return SuccessResponse({
            'message': 'Xóa bình luận thành công'
        },status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except CommentModel.DoesNotExist:
        return ErrorResponse({'message': 'Bình luận không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)