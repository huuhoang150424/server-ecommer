from .response import SuccessResponse
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'size'  
    max_page_size = 100 

    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params and self.page_size_query_param not in request.query_params:
            return None 

        return super().paginate_queryset(queryset, request, view)

    def get_pagination_response(self, data):
        return SuccessResponse({
            'totalItems': self.page.paginator.count if self.page else len(data),
            'currentPage': self.page.number if self.page else 1,
            'totalPages': self.page.paginator.num_pages if self.page else 1,
            'pageSize': self.page_size if self.page else len(data),
            'data': data
        })
