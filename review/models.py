from django.db import models
from product.models import ProductModel
from users.models import Users
import uuid

class RatingModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    rating = models.IntegerField()
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class CommentModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    comment = models.TextField()
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
