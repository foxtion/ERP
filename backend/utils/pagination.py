from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    标准分页器：支持 page/size 查询参数
    """
    # 默认每页数量
    page_size = 10
    # 前端控制每页数量的参数名
    page_size_query_param = 'size'
    # 最大每页数量
    max_page_size = 500
    # 页码参数名
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'list': data,
                'pagination': {
                    'page': self.page.number,
                    'size': self.page.paginator.per_page,
                    'total': self.page.paginator.count,
                }
            }
        })
