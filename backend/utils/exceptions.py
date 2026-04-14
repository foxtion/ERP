from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    自定义全局异常处理：将所有DRF异常统一包装为 {code, message, data} 格式
    """
    response = exception_handler(exc, context)

    if response is not None:
        # 处理DRF标准异常（如ValidationError、AuthenticationFailed等）
        message = response.data
        # 如果是字典或列表，尝试提取第一条错误信息作为message字符串
        if isinstance(message, dict):
            first_error = list(message.values())[0]
            if isinstance(first_error, list):
                message = first_error[0]
            else:
                message = str(first_error)
        elif isinstance(message, list):
            message = message[0]
        else:
            message = str(message)

        return Response({
            'code': response.status_code,
            'message': message,
            'data': response.data
        }, status=response.status_code)

    # 非DRF异常（如Python原生异常），返回500
    return Response({
        'code': 500,
        'message': '服务器内部错误：' + str(exc),
        'data': {}
    }, status=500)
