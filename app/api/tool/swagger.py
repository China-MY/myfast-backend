from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.openapi.utils import get_openapi
from starlette.responses import HTMLResponse
import json

from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.common.response import success, error

router = APIRouter()


@router.get("/json", summary="获取Swagger JSON")
async def get_swagger_json(
    request: Request,
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取Swagger JSON数据
    """
    try:
        app = request.app
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        return success(data=openapi_schema)
    except Exception as e:
        return error(msg=str(e))


@router.get("/ui", summary="Swagger UI页面")
async def get_swagger_ui():
    """
    返回Swagger UI页面
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI - Swagger UI</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/api/v1/tool/swagger/json",
                    dom_id: "#swagger-ui",
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    showExtensions: true,
                    showCommonExtensions: true
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content) 