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