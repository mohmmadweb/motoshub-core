"""Pagination that emits the `{data, links, meta}` envelope for list endpoints."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EnvelopePagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "links": {
                    "first": self.build_link(1),
                    "last": self.build_link(self.page.paginator.num_pages),
                    "next": self.get_next_link(),
                    "prev": self.get_previous_link(),
                },
                "meta": {
                    "count": self.page.paginator.count,
                    "page": self.page.number,
                    "pages": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
            }
        )

    def build_link(self, page_number):
        if not self.request:
            return None
        return self.replace_query_param_url(page_number)

    def replace_query_param_url(self, page_number):
        from rest_framework.utils.urls import replace_query_param

        url = self.request.build_absolute_uri()
        if page_number == 1:
            from rest_framework.utils.urls import remove_query_param

            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
