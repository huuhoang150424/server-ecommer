from rest_framework  import serializers
from .models import ProductModel,AttributesModel,ProductAttributesModel,FavoriteProductModel,StatusChoices
from category.serializers import GetCatSerializer


class createProductSerializers(serializers.ModelSerializer):
    product_name = serializers.CharField(max_length=50)
    price = serializers.FloatField() 
    thumb_image = serializers.CharField(max_length=300)
    stock = serializers.IntegerField() 
    image_urls = serializers.JSONField()  
    category_id = serializers.UUIDField()
    description = serializers.CharField(max_length=None, allow_blank=True)  
    attributes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )
    class Meta:
        model=ProductModel
        fields = [
            'product_name', 'price', 'thumb_image', 'stock', 
            'image_urls', 'category_id'
            , 'attributes','description'
        ]
    
    def validate(self, data):
        attributes = data.get("attributes", [])
        for attribute in attributes:
            attribute_name = attribute.get("attribute_name")
            if not attribute_name:
                raise serializers.ValidationError('Tên thuộc tính không được để trống.')
            if not AttributesModel.objects.filter(attribute_name=attribute_name).exists():
                print("Lỗi không tồn tại")
                raise serializers.ValidationError( f'Thuộc tính "{attribute_name}" không tồn tại.')
        if ProductModel.objects.filter(product_name=data['product_name']).exists():
            raise serializers.ValidationError('Sản phẩm đã tồn tại.')
        return data

    def create(self, data):
        attributes_data = data.pop('attributes', [])
        category_id = data.pop('category_id')
        product = ProductModel.objects.create(
            category_id=category_id,
            **data
        )
        for attribute_data in attributes_data:
            attribute_name = attribute_data.get('attribute_name')
            value = attribute_data.get('value')
            attribute = AttributesModel.objects.get(attribute_name=attribute_name)
            print(attribute)
            ProductAttributesModel.objects.create(
                product=product,
                attribute=attribute,
                value=value
            )
        return data


class getAllProductSerializers(serializers.ModelSerializer):
    class Meta:
        model=ProductModel
        fields='__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.attribute_name')

    class Meta:
        model = ProductAttributesModel
        fields = ['id', 'attribute_name', 'value'] 

class getProductSerializer(serializers.ModelSerializer):
    category = GetCatSerializer(read_only=True)
    product_attributes = ProductAttributeSerializer(many=True, read_only=True)
    class Meta:
        model=ProductModel
        fields = [
            'id', 'slug', 'product_name', 'price', 'thumb_image', 'stock',
            'image_urls', 'description', 'status', 'category',
            'product_attributes', 'created_at', 'updated_at'
        ]





class updateProductSerializers(serializers.ModelSerializer):
    product_name = serializers.CharField(max_length=50)
    price = serializers.FloatField() 
    thumb_image = serializers.CharField(max_length=300)
    stock = serializers.IntegerField() 
    image_urls = serializers.JSONField()  
    category_id = serializers.UUIDField()
    description = serializers.CharField(max_length=None, allow_blank=True)  
    status = serializers.ChoiceField(
        choices=StatusChoices.choices,  
        default=StatusChoices.AVAILABLE  
    )
    attributes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )
    class Meta:
        model=ProductModel
        fields=[
            'product_name', 'price', 'thumb_image', 'stock', 
            'image_urls', 'category_id'
            , 'attributes','status','description'
        ]
    def validate(self,data):
        id=self.context.get('id')
        print(id)
        if not ProductModel.objects.filter(id=id).exists():
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return data




class deleteProductSerializers(serializers.ModelSerializer):

    class Meta:
        model=ProductModel
        fields='__all__'
    
    def create(self,data):
        pass
    def validate(self,data):
        pass


class getCommentProductSerializers(serializers.ModelSerializer):

    class Meta:
        model=ProductModel
        fields='__all__'
    
    def create(self,data):
        pass
    def validate(self,data):
        pass



#Attribute
class createAttributesSerializers(serializers.ModelSerializer):

    attribute_name = serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model=AttributesModel
        fields=['attribute_name']
    
    def create(self,data):
        newAttribute=AttributesModel.objects.create(**data)
        return newAttribute
    def validate(self,data):
        if AttributesModel.objects.filter(attribute_name=data['attribute_name']).exists():
            raise serializers.ValidationError('Thuộc tính này đã tồn tại')

        return data



class getAllAttributesSerializers(serializers.ModelSerializer):

    class Meta:
        model=AttributesModel
        fields=['id','attribute_name']



class updateAttributesSerializers(serializers.ModelSerializer):
    attribute_name = serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model=AttributesModel
        fields=['id','attribute_name']
    
    def validate(self,data):
        attribute_id=self.context.get('id')

        if not AttributesModel.objects.filter(id=attribute_id).exists():
            raise serializers.ValidationError('Thuộc tính này không tồn tại')

        return data