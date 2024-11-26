from django.db import models
from product.models import ProductModel
from users.models import Users
import uuid

class ReviewModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    rating = models.IntegerField() 
    comment = models.TextField()    
    # product = models.ForeignKey(
    #     ProductModel, 
    #     on_delete=models.CASCADE,  
    #     related_name='reviews' 
    # )
    # user = models.ForeignKey(
    #     Users, 
    #     on_delete=models.CASCADE, 
    #     related_name='reviews'  
    # )
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f"Review by {self.user} on {self.product}"
    
    class Meta:
        db_table = 'review'  
        ordering = ['-created_at'] 
