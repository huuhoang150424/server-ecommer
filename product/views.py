from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from users.decorator import admin_required,user_required
from .serializers import *
from utils.response import SuccessResponse,ErrorResponse
from django.core.paginator import Paginator
from utils.pagination import CustomPagination
from .models import ProductModel,AttributesModel



@api_view(['GET'])
@user_required  
def getAllProducts(request):
    try:
        allProduct=ProductModel.objects.all().order_by('id')
        paginator=CustomPagination()
        paginated_data=paginator.paginate_queryset(allProduct, request)
        if paginated_data is None:  
            product_serializer = getAllProductSerializers(allProduct, many=True)
            return SuccessResponse({
                'totalItems': len(allProduct),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(allProduct),
                'data': product_serializer.data
            })

        product_serializer = getAllProductSerializers(paginated_data, many=True)
        return paginator.get_pagination_response(product_serializer.data)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_required  
def getProduct(request,slug):
    try:
        product = ProductModel.objects.prefetch_related('product_attributes__attribute').select_related('category').get(slug=slug)
        product_serializer = getProductSerializer(product)
        return SuccessResponse({
            'data': product_serializer.data
        }, status=status.HTTP_200_OK) 
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@admin_required  
def createProduct(request):
    try:
        serializer = createProductSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse(
                {'message': 'Tạo sản phẩm mới thành công'}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@admin_required  
def editProduct(request,id):
    try:
        product=ProductModel.objects.get(id=id)
        print(product)
        serializer=updateProductSerializers(
            instance=product,
            data=request.data,
            context={'id': id}
        )
        if serializer.is_valid():
            serializer.save() 
            return SuccessResponse({
                'message': 'Cập nhật sản phẩm thành công'
            }, status=status.HTTP_200_OK)
            
        return ErrorResponse({
            'message': 'Dữ liệu không hợp lệ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@admin_required  
def deleteProduct(request,id):
    try:
        if not ProductModel.objects.filter(id=id).exists():
            return ErrorResponse({
                'message': 'Không tìm thấy sản phẩm'
            },status=status.HTTP_404_NOT_FOUND)
        product = ProductModel.objects.get(id=id)
        product.delete()
        
        return SuccessResponse(
            {'message': 'Sản phẩm đã được xóa thành công'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Attribute
@api_view(['POST'])
@admin_required  
def createAttribute(request):
    try:
        attribute_serializer=createAttributesSerializers(data=request.data)
        if attribute_serializer.is_valid():
            attribute_serializer.save()
            return SuccessResponse(
                {'message': 'Tạo thuộc tính mới thành công'}, 
                status=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            {'errors': attribute_serializer.errors, 'message': 'Tạo thư mục mới thất bại'}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@admin_required  
def updateAttribute(request,id):
    try:
        attribute=AttributesModel.objects.get(id=id)
        attribute_serializer=updateAttributesSerializers(
            instance=attribute,
            data=request.data,
            context={'id':id}
        )
        if attribute_serializer.is_valid():
            attribute_serializer.save()
            return SuccessResponse(
                {'message': 'Cập nhật thuộc tính thành công'}, 
                status=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            {'errors': attribute_serializer.errors, 'message': 'Cập nhật thuộc tính thất bại'}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@admin_required  
def getAllAttribute(request):
    try:
        allAttribute=AttributesModel.objects.all().order_by('id')
        paginator=CustomPagination()
        paginated_data=paginator.paginate_queryset(allAttribute,request)
        if paginated_data is None:  
            attribute_serializers=getAllAttributesSerializers(allAttribute,many=True)
            return SuccessResponse({
                'totalItems': len(allAttribute),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(allAttribute),
                'data': attribute_serializers.data
            })
        attribute_serializers=getAllAttributesSerializers(paginated_data,many=True)

        return paginator.get_pagination_response(attribute_serializers.data)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@admin_required  
def deleteAttribute(request,id):
    try:
        if not AttributesModel.objects.filter(id=id).exists():
            return ErrorResponse(
                {'message': 'Thuộc tính không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )
        attribute=AttributesModel.objects.filter(id=id)
        attribute.delete()
        return SuccessResponse({
            'message': 'Xóa thuộc tính thành công'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)