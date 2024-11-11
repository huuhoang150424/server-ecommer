from django.db import models
import uuid



class CategoryModel(models.Model):
    id=models.UUIDField(
        primary_key=True,
        editable=True,
        default=uuid.uuid4
    )
    category_name=models.CharField(max_length=50)
    image=models.CharField( max_length=250)

    def __str__(self):
        return f"{self.category_name}"
    
    class Meta:
        db_table='category'

