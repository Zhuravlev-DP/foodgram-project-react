from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинатор вывода количества объектов и номера страницы."""
    page_size_query_param = 'limit'
