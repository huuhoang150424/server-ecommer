from rest_framework  import serializers
from users.models import Users
from order.models import orderModel
from review.models import RatingModel,CommentModel
from product.models import ProductModel



class GetUserBuyProductSoMuchSerializer(serializers.ModelSerializer):
    order_count = serializers.IntegerField()

    class Meta:
        model = Users
        fields = ['name', 'email', 'avatar', 'order_count']