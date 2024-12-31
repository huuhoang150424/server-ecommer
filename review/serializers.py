from rest_framework import serializers
from .models import  RatingModel,CommentModel
from product.models import ProductModel


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['comment', 'product', 'user']
        extra_kwargs = {
            'comment': {'required': True},
            'product': {'required': True},
            'user': {'required': True},
        }


class getCommentSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = CommentModel
        fields = ['id','comment', 'created_at', 'user_info']  

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name,
            'email': obj.user.email,
            'avatar': obj.user.avatar  
        }

class updateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentModel
        fields = ['comment', 'update_at']  

    def validate(self,data):
        if not CommentModel.objects.filter(id=self.context.get('id')).exists():
            raise serializers.ValidationError('Bình luận không tồn tại')
        return data



class getRatingSerializer(serializers.ModelSerializer):
    user_info= serializers.SerializerMethodField()
    class Meta:
        model = RatingModel
        fields = ['rating','created_at','user_info']
        
    def get_user_info(self, obj):
        return {
            'id': obj.user.id 
        }

class getReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    class Meta:
        model = RatingModel
        fields = ['product', 'user', 'rating', 
        'comment'
        ]

    def get_user(self, obj):
        return {
            'avatar': obj.user.avatar,
            'name': obj.user.name
        }

    def get_product(self, obj):
        return {
            'product_name': obj.product.product_name,
            'thumb_image': obj.product.thumb_image
        }

    def get_comment(self, obj):
        comment = CommentModel.objects.filter(
            product=obj.product, user=obj.user
        ).first() 
        return comment.comment if comment else ""