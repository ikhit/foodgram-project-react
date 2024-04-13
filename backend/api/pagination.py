from rest_framework.pagination import PageNumberPagination

from foodgram.const import PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    """Кастоманя пагинцаия для сервиса."""

    page_size = PAGE_SIZE
    page_size_query_param = "limit"
