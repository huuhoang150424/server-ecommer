####
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user and getattr(request.user, 'isAdmin', False):
            return view_func(request, *args, **kwargs)
        return Response({"message": "Bạn không có quyền của admin"}, status=status.HTTP_403_FORBIDDEN)
    return _wrapped_view


def user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user :
            return view_func(request, *args, **kwargs)
        return Response({"message": "Bạn không có quyền của user"}, status=status.HTTP_403_FORBIDDEN)
    return _wrapped_view
    
