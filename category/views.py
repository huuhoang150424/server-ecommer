from .models import CategoryModel
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from users.decorator import admin_required,user_required
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from django.core.paginator import Paginator
from utils.pagination import CustomPagination
from django.db.models import Count,Sum

@api_view(['GET'])
@user_required  
def getAllCat(request):
    try:
        allCategory = CategoryModel.objects.all().order_by('id')
        paginator = CustomPagination()
        paginated_data = paginator.paginate_queryset(allCategory, request)
        if paginated_data is None:  
            category_serializer = getAllCatSerializers(allCategory, many=True)
            return SuccessResponse({
                'totalItems': len(allCategory),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(allCategory),
                'data': category_serializer.data
            },status=status.HTTP_200_OK)
        category_serializer = getAllCatSerializers(paginated_data, many=True)
        return paginator.get_pagination_response(category_serializer.data)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@admin_required
def createCat(request):
    try: 
        createCat_serializers=createCatSerializers(data=request.data)
        if createCat_serializers.is_valid():
            createCat_serializers.save()
            return SuccessResponse(
                {'message': 'Tạo danh mục mới thành công'}, 
                status=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            {'errors': createCat_serializers.errors, 'message': 'Tạo thư mục mới thất bại'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@admin_required
def deleteCat(request, catId):
    try:
        category = CategoryModel.objects.get(id=catId)
        category.delete()
        return SuccessResponse(
            {'message': 'Danh mục đã được xóa thành công'},
            status=status.HTTP_200_OK
        )
    except CategoryModel.DoesNotExist:
        return ErrorResponse({'message':'Danh mục không tồn tại'},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@user_required
def getCat(request, catId): 
    try:
        category = CategoryModel.objects.get(id=catId)
        serializer = GetCatSerializer(category, context={'catId': catId})
        return SuccessResponse({
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Danh mục không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message="Lỗi không xác định", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@admin_required
def updateCat(request,catId):
    try: 

        category = CategoryModel.objects.get(id=catId)
        category.category_name=request.data.get("category_name")
        category.image=request.data.get("image")
        category.save()
        return Response({
            'message': 'Cập nhật danh mục thành công'
        }, status=status.HTTP_200_OK)
            
    except CategoryModel.DoesNotExist:
        return ErrorResponse({'message': 'Danh mục không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error_message': str(e),
            'message': 'Đã xảy ra lỗi trong quá trình xử lý'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required
def getAllClient(request): 
    try:
        category = CategoryModel.objects.annotate(product_count=Count('products')).order_by('-product_count')[:5]
        serializer = GetCatClientSerializer(category,many=True)
        return SuccessResponse({
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message="Lỗi không xác định", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
