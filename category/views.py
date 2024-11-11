from .models import CategoryModel
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from users.decorator import admin_required,user_required
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse


@api_view(['GET'])
@user_required  
def getAllCat(request):
    try:
        allCategory = CategoryModel.objects.all()
        category_serializer = getAllCatSerializers(allCategory, many=True)
        return SuccessResponse(data=category_serializer.data)
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
                {'message': 'Tạo thư mục mới thành công'}, 
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
        if not CategoryModel.objects.filter(id=catId).exists():
            return ErrorResponse(
                {'message': 'Danh mục không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        category = CategoryModel.objects.get(id=catId)
        category.delete()
        
        return SuccessResponse(
            {'message': 'Danh mục đã được xóa thành công'},
            status=status.HTTP_200_OK
        )
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
            'message': 'Danh mục được tìm thấy'
        }, status=status.HTTP_200_OK)
    except CategoryModel.DoesNotExist:
        return Response({
            'message': 'Danh mục không tồn tại'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error_message': str(e),
            'message': 'Đã xảy ra lỗi trong quá trình xử lý'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@admin_required
def updateCat(request):
    pass