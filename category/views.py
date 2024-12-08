from .models import CategoryModel
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from users.decorator import admin_required,user_required
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from django.core.paginator import Paginator
from utils.pagination import CustomPagination


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
            })
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
        if serializer.is_valid():
            return SuccessResponse({
                'data': serializer.data,
                'message': 'Danh mục được tìm thấy'
            }, status=status.HTTP_200_OK)
        return ErrorResponse({
            'message': 'Thất bại',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error_message': str(e),
            'message': 'Đã xảy ra lỗi trong quá trình xử lý'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@admin_required
def updateCat(request,catId):
    try: 
        category = CategoryModel.objects.get(id=catId)
        serializer = updateCatSerializers(
            instance=category,  
            data=request.data, 
            context={'catId': catId}  
        )
        if serializer.is_valid():
            serializer.save() 
            return Response({
                'message': 'Cập nhật danh mục thành công'
            }, status=status.HTTP_200_OK)
            
        return ErrorResponse({
            'message': 'Dữ liệu không hợp lệ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error_message': str(e),
            'message': 'Đã xảy ra lỗi trong quá trình xử lý'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

