"""
Custom Pagination Classes for API
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with page size of 20
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        body = {
            "success": True,
            "data": data,
            "pagination": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.page_size,
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
            },
        }

        response = Response(body)

        try:
            base_url = self.request.build_absolute_uri()
            first_url = replace_query_param(base_url, self.page_query_param, 1)
            last_url = replace_query_param(base_url, self.page_query_param, self.page.paginator.num_pages)
            next_url = self.get_next_link()
            prev_url = self.get_previous_link()

            links = []
            if first_url:
                links.append(f"<{first_url}>; rel=\"first\"")
            if last_url:
                links.append(f"<{last_url}>; rel=\"last\"")
            if next_url:
                links.append(f"<{next_url}>; rel=\"next\"")
            if prev_url:
                links.append(f"<{prev_url}>; rel=\"prev\"")

            if links:
                response["Link"] = ", ".join(links)
            response["X-Total-Count"] = str(self.page.paginator.count)
        except Exception:
            pass

        return response


class LargeResultsSetPagination(PageNumberPagination):
    """
    Large pagination with page size of 100
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500

    def get_paginated_response(self, data):
        body = {
            "success": True,
            "data": data,
            "pagination": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.page_size,
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
            },
        }

        response = Response(body)

        try:
            base_url = self.request.build_absolute_uri()
            first_url = replace_query_param(base_url, self.page_query_param, 1)
            last_url = replace_query_param(base_url, self.page_query_param, self.page.paginator.num_pages)
            next_url = self.get_next_link()
            prev_url = self.get_previous_link()

            links = []
            if first_url:
                links.append(f"<{first_url}>; rel=\"first\"")
            if last_url:
                links.append(f"<{last_url}>; rel=\"last\"")
            if next_url:
                links.append(f"<{next_url}>; rel=\"next\"")
            if prev_url:
                links.append(f"<{prev_url}>; rel=\"prev\"")

            if links:
                response["Link"] = ", ".join(links)
            response["X-Total-Count"] = str(self.page.paginator.count)
        except Exception:
            pass

        return response
