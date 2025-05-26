from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с переименованным параметром размера страницы."""

    page_size_query_param = 'limit'
    max_page_size = 100
