import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义全局异常处理：将所有DRF异常统一包装为 {code, message, data} 格式
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = response.data
        if isinstance(message, dict):
            if message:
                first_error = next(iter(message.values()))
                if isinstance(first_error, list) and first_error:
                    message = first_error[0]
                else:
                    message = str(first_error)
            else:
                message = '请求参数错误'
        elif isinstance(message, list):
            if message:
                message = message[0]
            else:
                message = '请求参数错误'
        else:
            message = str(message)

        return Response({
            'code': response.status_code,
            'message': message,
            'data': response.data
        }, status=response.status_code)

    # DEBUG 模式下返回详细错误信息，方便定位问题
    from django.conf import settings
    if settings.DEBUG:
        import traceback
        tb = traceback.format_exc()
        message = f'{str(exc)}\n{tb}'
    else:
        message = '服务器内部错误'
    logger.exception('服务器内部错误: %s', exc)
    return Response({
        'code': 500,
        'message': message,
        'data': {}
    }, status=500)
