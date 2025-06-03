import time
import logging
import json
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 配置日志格式
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件
    记录请求日志和响应日志
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取请求信息
        path = request.url.path
        method = request.method
        query = dict(request.query_params)
        client_ip = request.client.host if request.client else None
        
        # 记录请求日志
        log_dict = {
            "request_path": path,
            "request_method": method,
            "request_query": query,
            "client_ip": client_ip
        }

        # 记录请求体 (如果是POST/PUT等方法且不是文件上传类型)
        if method in ["POST", "PUT", "PATCH"] and not request.headers.get("content-type", "").startswith("multipart/form-data"):
            try:
                body = await request.body()
                if body:
                    try:
                        # 尝试解析JSON
                        log_dict["request_body"] = json.loads(body)
                    except:
                        # 如果不是JSON，则记录字符串形式
                        log_dict["request_body"] = body.decode("utf-8")
            except Exception as e:
                log_dict["request_body_error"] = str(e)
        
        logger.info(f"REQUEST: {json.dumps(log_dict, ensure_ascii=False)}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 记录响应信息
            process_time = time.time() - start_time
            response_log = {
                "request_path": path,
                "response_status": response.status_code,
                "process_time": f"{process_time:.4f}s"
            }
            
            logger.info(f"RESPONSE: {json.dumps(response_log, ensure_ascii=False)}")
            
            return response
        except Exception as e:
            # 异常记录
            process_time = time.time() - start_time
            error_log = {
                "request_path": path,
                "error": str(e),
                "process_time": f"{process_time:.4f}s"
            }
            logger.error(f"ERROR: {json.dumps(error_log, ensure_ascii=False)}")
            raise 