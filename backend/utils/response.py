from rest_framework.response import Response


def success_response(data=None, message='操作成功', code=200):
    """
    统一的成功响应格式
    :param data: 响应数据
    :param message: 提示信息
    :param code: 业务状态码，默认200
    """
    return Response({
        'code': code,
        'message': message,
        'data': data if data is not None else {}
    })


def error_response(message='操作失败', code=400, data=None):
    """
    统一的错误响应格式
    :param message: 错误提示
    :param code: 业务状态码，默认400
    :param data: 可选的错误详情数据
    """
    return Response({
        'code': code,
        'message': message,
        'data': data if data is not None else {}
    }, status=code)
