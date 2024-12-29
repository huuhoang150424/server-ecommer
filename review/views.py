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
from rest_framework.pagination import LimitOffsetPagination

@api_view(['POST'])
@user_required
def ratingProduct(request, productId):
    try:
        product = get_object_or_404(ProductModel, id=productId)
        countStar = request.data.get('rating')
        if countStar is None:
            return ErrorResponse({'error': 'Rating bắt buộc.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        rating = RatingModel.objects.filter(user=user, product=product).first()
        if rating:
            rating.rating = countStar
            rating.save()
            return SuccessResponse({
                'message': 'Đánh giá đã được cập nhật thành công.'
            }, status=status.HTTP_200_OK)
        else:
            new_rating = RatingModel.objects.create(user=user, product=product, rating=countStar)
            new_rating.save()
            return SuccessResponse({
                'message': 'Đánh giá thành công.'
            }, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        return ErrorResponse(error_message=f"Database integrity error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@user_required
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

class CommentPagination(LimitOffsetPagination):
    default_limit = 5  
    max_limit = 30

@api_view(['GET'])
@user_required
def getCommentProduct(request, productId):
    try:
        comments = CommentModel.objects.filter(product=productId).select_related('user').order_by('-created_at')
        
        paginator = CommentPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)

        serializer = getCommentSerializer(paginated_comments, many=True)

        return SuccessResponse({
            'results': serializer.data,
            'has_next': paginator.get_next_link() is not None,
            'next_offset': paginator.offset + paginator.limit if paginator.get_next_link() else None,
            'count': len(comments),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@user_required
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
@user_required
def deleteComment(request, id):
    try:
        user =request.user
        comment = CommentModel.objects.get(id=id)
        print(comment.user.id)
        if comment.user.id!=user.id:
            return ErrorResponse({'message': 'Bạn không thể xóa bình luận của người khác'}, status=status.HTTP_400_BAD_REQUEST)
        comment.delete()
        return SuccessResponse({
            'message': 'Xóa bình luận thành công'
        },status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except CommentModel.DoesNotExist:
        return ErrorResponse({'message': 'Bình luận không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)