from rest_framework  import serializers
from .models import orderDetailModel,orderModel,orderHistoryModel
from users.serializers import getUserSeriaLizer
from product.models import ProductModel
from category.serializers import GetCatSerializer



class ProductSerializer(serializers.ModelSerializer):
    category=GetCatSerializer(read_only=True)

    class Meta:
        model = ProductModel
        fields = ['product_name', 'price', 'thumb_image','stock','category']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  
    class Meta:
        model = orderDetailModel
        fields = ['id','product', 'quantity', 'price']



class OrderSerializer(serializers.ModelSerializer):
    user=serializers.SerializerMethodField()
    class Meta:
        model = orderModel
        fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'shipping_address','receiver_name','receiver_phone','order_code']
    def get_user(self, obj):
        if obj.user:
            return {
                'name': obj.user.name,
                'email': obj.user.email
            }
        return None

class OrderByUserSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True) 
    class Meta:
        model = orderModel
        fields = ['id', 'total_amount', 'status', 'created_at', 'order_details','shipping_address','receiver_name','receiver_phone','order_code']
    def get_order_details(self, obj):
        return obj

class OrderHistoryByUserSerializer(serializers.ModelSerializer):
    order = OrderByUserSerializer( read_only=True) 
    class Meta:
        model = orderHistoryModel
        fields = [ 'id',  'status',  'changed_at',  'order', 'end_time']
    def get_order_details(self, obj):
        return obj

class OrderHistoryByOrderSerializer(serializers.ModelSerializer):
    change_by = serializers.SerializerMethodField()

    class Meta:
        model = orderHistoryModel
        fields = ['id', 'status', 'changed_at', 'order', 'end_time', 'change_by']

    def get_change_by(self, obj):
        user = obj.change_by
        if user:
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        return None



class OrderHistorySerializer(serializers.ModelSerializer):
    order_histories = OrderHistoryByOrderSerializer(many=True, read_only=True)

    class Meta:
        model = orderModel
        fields = ['id', 'order_histories']



class ListOrderChangeSerializer(serializers.ModelSerializer):
    change_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = orderHistoryModel
        fields = ['id','change_by','status','changed_at']
    def get_change_by(self, obj):
        user = obj.change_by
        if user:
            return {
                'name': user.name,
                'avatar': user.avatar
            }
        return None
    def get_status(self, obj):
            return obj.get_status_display()  # trả về dạng tiếng việt cho status