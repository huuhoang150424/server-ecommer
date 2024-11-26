from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Users
from django.core.cache import cache



class JWTAuthenticatedMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('token')
        if token and token.startswith('Bearer '):
            try:
                JWTToken = token.split(' ')[1]
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(JWTToken)
                user_id = validated_token['user_id']
                # get user for cache
                user = cache.get(f"user_{user_id}")
                if not user:
                    user = Users.objects.get(id=user_id)
                    cache.set(f"user_{user_id}", user, timeout=60*60)
                request.user = user
                request._user = user
            except Exception as e:
                request.user = None
                request._user = None
        else:
            print("No valid Authorization header found")
            request.user = None
            request._user = None

        response = self.get_response(request)
        return response
