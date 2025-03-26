from rest_framework  import serializers
from .models import CategoryModel


class createCatSerializers(serializers.ModelSerializer):
    category_name=serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model=CategoryModel
        fields=['category_name','image']
    def create(self,data):
        print("data", data)
        newCategory=CategoryModel.objects.create(**data)
        return newCategory
    def validate(self,validated_data):
        if CategoryModel.objects.filter(category_name=validated_data['category_name']).exists():
            raise serializers.ValidationError('Danh mục đã tồn tại')
        return validated_data

class getAllCatSerializers(serializers.ModelSerializer):
    class Meta:
        model=CategoryModel
        fields=['id','category_name','image']

class getAllProductByCatSerializers(serializers.ModelSerializer):
    class Meta:
        model=CategoryModel
        fields=['id','category_name','image']


class GetCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['id','category_name', 'image']

    def validate(self, validated_data):
        catId = self.context.get('catId')
        if not CategoryModel.objects.filter(id=catId).exists():
            raise serializers.ValidationError("Danh mục không tồn tại")
        return validated_data

class GetCatClientSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField()
    class Meta:
        model = CategoryModel
        fields = ['id','category_name', 'product_count']
