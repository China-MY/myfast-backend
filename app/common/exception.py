from fastapi import HTTPException, status


class APIException(HTTPException):
    """API异常基类"""
    def __init__(
        self,
        detail: str = "未知错误",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFound(APIException):
    """资源未找到异常"""
    def __init__(self, detail: str = "资源未找到"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class BadRequest(APIException):
    """请求参数错误异常"""
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class Unauthorized(APIException):
    """未授权异常"""
    def __init__(self, detail: str = "未授权"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class Forbidden(APIException):
    """权限不足异常"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ServerError(APIException):
    """服务器内部错误异常"""
    def __init__(self, detail: str = "服务器内部错误"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 