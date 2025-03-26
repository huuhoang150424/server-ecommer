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
from category.models import CategoryModel
from django.db.models import Q,Max,Count, Subquery, OuterRef,Avg,Min,Q,Exists , Case, When,F,Min
from review.models import RatingModel

from django_redis import get_redis_connection
redis_conn = get_redis_connection('default')
import json





@api_view(['GET'])
@user_required
def getProductClient(request, id):
    try:
        cache_key = f'product_{id}'
        cached_product = redis_conn.get(cache_key)
        
        if cached_product:
            return SuccessResponse({
                'data': json.loads(cached_product.decode('utf-8'))  
            }, status=status.HTTP_200_OK)
        product = ProductModel.objects.prefetch_related(
            'product_attributes__attribute', 'ratings'
        ).select_related('category').get(id=id)
        product_serializer = getProductSerializerClient(product, context={'user': request.user})
        # Chuyển UUID thành chuỗi trước khi lưu vào cache
        try:
            redis_conn.setex(cache_key, 3600, json.dumps(product_serializer.data, default=str))
            print(f"Lưu thành công key vào Redis: {cache_key}")
        except Exception as redis_error:
            print(f"Lỗi khi lưu vào Redis: {redis_error}")
        # default=str giúp chuyển UUID thành chuỗi
        return SuccessResponse({
            'data': product_serializer.data
        }, status=status.HTTP_200_OK)
    except ProductModel.DoesNotExist:
        return ErrorResponse(error_message="Sản phẩm không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required
def getAllProducts(request):
    try:
        offset = int(request.GET.get('offset', 0))  
        limit = int(request.GET.get('limit', 10))  
        cache_key = f'products_{offset}_{limit}'
        cached_data = redis_conn.get(cache_key)
        if cached_data:
            return SuccessResponse({
                'data': json.loads(cached_data),  
                'fromCache': True,
            }, status=status.HTTP_200_OK)
        allProduct = ProductModel.objects.all().order_by('id')
        paginator = CustomPagination()
        paginated_data = paginator.paginate_queryset(allProduct, request)
        if paginated_data is None:
            product_serializer = getAllProductSerializers(allProduct, many=True)
            redis_conn.setex(cache_key, 3600, json.dumps(product_serializer.data, default=str))  
            return SuccessResponse({
                'totalItems': len(allProduct),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(allProduct),
                'data': product_serializer.data
            })
        product_serializer = getAllProductSerializers(paginated_data, many=True)
        total_items = allProduct.count()
        page_size = paginator.page_size
        total_pages = (total_items + page_size - 1) // page_size
        current_page = paginator.page
        redis_conn.setex(cache_key, 3600, json.dumps(product_serializer.data, default=str))  
        return paginator.get_pagination_response({
            'totalItems': total_items,
            'currentPage': current_page,
            'totalPages': total_pages,
            'pageSize': page_size,
            'data': product_serializer.data
        })
    except Exception as e:
        print(e)
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#search list key product
@api_view(['GET'])
@user_required
def similar(request):
    try:
        keyword = request.GET.get('keyword', '').lower()
        if not keyword:
            return Response({"error": "Keyword parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        products = ProductModel.objects.filter(product_name__icontains=keyword)
        if not products.exists():
            return SuccessResponse({"result": []}, status=status.HTTP_200_OK)
        list_keyword = [product.product_name for product in products]
        return SuccessResponse({
            'data': list_keyword
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse({"success": False, "status": 500, "error_message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#search  key product
@api_view(['GET'])
@user_required  
def search(request):
    try:
        keyword=request.GET.get('keyword','').lower()
        products=ProductModel.objects.filter(product_name__icontains=keyword)
        product_serializer=searchProductSerializer(products,many=True)
        
        list_keyword = [product.product_name for product in products]
        print(list_keyword)
        return SuccessResponse({
            'data': product_serializer.data,
            'keyword': list_keyword
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@user_required  
def getProductRecent(request):
    try:
        cache_key = 'recent_products'
        cached_data = redis_conn.get(cache_key) 
        
        if cached_data:
            return SuccessResponse({
                'data': json.loads(cached_data)  # Giải mã dữ liệu JSON từ cache
            }, status=status.HTTP_200_OK)
        allProduct = ProductModel.objects.order_by('-created_at')[:10]
        product_serializer = getAllProductRecentSerializers(allProduct, many=True)
        serialized_data = json.dumps(product_serializer.data, default=str) # chuyển đối tượng thành chuỗi
        redis_conn.setex(cache_key, 3600, serialized_data)
        return SuccessResponse({
            'data': product_serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
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
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(
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


#favorite product
@api_view(['POST'])
@user_required  
def addFavoriteProduct(request):
    try:
        user = request.user
        product_id = request.data.get('productId') 
        product = ProductModel.objects.get(id=product_id)
        add_product_favorite_serializer = productFavorite(data={'user': user.id, 'product': product.id})
        if add_product_favorite_serializer.is_valid():
            add_product_favorite_serializer.save()
            return SuccessResponse(
                {'message': 'Thêm sản phẩm yêu thích thành công'}, 
                status=status.HTTP_201_CREATED
            )
        
        return ErrorResponse(
            {'errors': add_product_favorite_serializer.errors, 'message': 'Thêm sản phẩm yêu thích thất bại'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@user_required
def removeFavoriteProduct(request):
    try:
        user = request.user
        product_id = request.data.get('productId')
        if not product_id:
            return Response({"message": "Vui lòng cung cấp ID sản phẩm."}, status=status.HTTP_400_BAD_REQUEST)
        favorite_product = FavoriteProductModel.objects.filter(user=user, product_id=product_id)
        if favorite_product.exists():
            favorite_product.delete()
            return SuccessResponse(
                {'message': 'Xóa sản phẩm yêu thích thành công'},
                status=status.HTTP_200_OK
            )
        else:
            return ErrorResponse(
                {'message': 'Sản phẩm yêu thích không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required  
def getAllFavoriteProduct(request):
    try:
        user = request.user
        allFavoriteProduct=FavoriteProductModel.objects.prefetch_related('product').filter(user=user)


        serializers=getAllProductFavorite(allFavoriteProduct,many=True)
        return SuccessResponse(
            {'message': 'Thành công', 'data': serializers.data}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#filter
@api_view(['GET'])
@user_required
def getProductByCat(request, categoryId):
    try:
        products = ProductModel.objects.filter(category_id=categoryId)  
        serializers = getProductSerializer(products, many=True)
        return SuccessResponse( {'message': 'Thành công', 'data': serializers.data}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse( error_message=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required
def getProductByPrice(request):
    try:
        min_price = request.GET.get('minPrice', None)
        max_price = request.GET.get('maxPrice', None)
        if min_price is None or max_price is None:
            return ErrorResponse(
                {"ErrorResponse": "Vui lòng cung cấp minPrice và maxPrice"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            min_price = float(min_price)
            max_price = float(max_price)
        except ValueError:
            return ErrorResponse(
                {"message": "minPrice và maxPrice phải là số hợp lệ"},
                status=status.HTTP_400_BAD_REQUEST
            )
        products = ProductModel.objects.filter(
            Q(price__gte=min_price) & Q(price__lte=max_price) 
        )
        serializer = searchProductSerializer(products, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# lấy sản phẩm có đánh giá không thấp hơn countStar
@api_view(['GET'])
@user_required
def getProductByStar(request):
    try:
        countStar = request.GET.get('countStar', None)
        products = ProductModel.objects.annotate(
            min_rating=Min('ratings__rating') #lấy số sao nhỏ nhất của sản phẩm đó
        ).filter(
            min_rating__lte=countStar
        )
        serializer = searchProductSerializer(products, many=True)
        return SuccessResponse(
            {"message": "Thành công", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)