from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from fastapi import APIRouter, Depends, Path, Body, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.common.response import success, error, page

# 定义泛型类型变量
T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
QuerySchemaType = TypeVar('QuerySchemaType', bound=BaseModel)


class RestApiBase(Generic[T, CreateSchemaType, UpdateSchemaType, QuerySchemaType]):
    """
    RESTful API基础类
    提供标准的CRUD操作和响应格式
    """
    def __init__(
        self,
        *,
        router: APIRouter,
        service,
        prefix: str,
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        query_schema: Type[QuerySchemaType],
        tags: List[str],
        id_field: str = "id",
        auth_required: bool = True
    ):
        self.router = router
        self.service = service
        self.prefix = prefix
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.query_schema = query_schema
        self.tags = tags
        self.id_field = id_field
        self.auth_required = auth_required
        
        # 注册路由
        self.register_routes()
    
    def get_list_endpoint(self) -> Callable:
        """创建获取列表的端点函数"""
        query_model = self.query_schema
        
        async def endpoint(
            db: Session = Depends(get_db),
            params: query_model = Depends(),
        ):
            try:
                items, total = self.service.get_list(db, params)
                return page(rows=items, total=total)
            except Exception as e:
                return error(msg=str(e))
                
        return endpoint
    
    def get_item_endpoint(self) -> Callable:
        """创建获取详情的端点函数"""
        async def endpoint(
            item_id: Any = Path(...),
            db: Session = Depends(get_db),
        ):
            try:
                item = self.service.get_by_id(db, item_id)
                if not item:
                    return error(msg=f"{self.prefix}不存在", code=404)
                return success(data=item)
            except Exception as e:
                return error(msg=str(e))
        
        return endpoint
    
    def create_item_endpoint(self) -> Callable:
        """创建新增的端点函数"""
        create_model = self.create_schema
        
        async def endpoint(
            item_data: create_model,
            db: Session = Depends(get_db),
        ):
            try:
                item = self.service.create(db, item_data)
                return success(data=item, msg=f"{self.prefix}创建成功")
            except ValueError as e:
                return error(msg=str(e), code=400)
            except Exception as e:
                return error(msg=str(e))
        
        return endpoint
    
    def update_item_endpoint(self) -> Callable:
        """创建更新的端点函数"""
        update_model = self.update_schema
        
        async def endpoint(
            item_id: Any = Path(...),
            item_data: update_model = Body(...),
            db: Session = Depends(get_db),
        ):
            try:
                item = self.service.update(db, item_id, item_data)
                return success(data=item, msg=f"{self.prefix}更新成功")
            except ValueError as e:
                return error(msg=str(e), code=400)
            except HTTPException as e:
                return error(msg=e.detail, code=e.status_code)
            except Exception as e:
                return error(msg=str(e))
        
        return endpoint
    
    def delete_item_endpoint(self) -> Callable:
        """创建删除的端点函数"""
        async def endpoint(
            item_id: Any = Path(...),
            db: Session = Depends(get_db),
        ):
            try:
                result = self.service.delete(db, item_id)
                return success(msg=f"{self.prefix}删除成功")
            except HTTPException as e:
                return error(msg=e.detail, code=e.status_code)
            except Exception as e:
                return error(msg=str(e))
        
        return endpoint
        
    def register_routes(self):
        """注册标准RESTful路由"""
        # 设置依赖项
        dependencies = None
        if self.auth_required:
            dependencies = [Depends(get_current_active_user)]
            
        # 获取列表
        self.router.add_api_route(
            path=f"/{self.prefix}",
            endpoint=self.get_list_endpoint(),
            methods=["GET"],
            summary=f"获取{self.prefix}列表",
            tags=self.tags,
            dependencies=dependencies,
        )
        
        # 获取详情
        self.router.add_api_route(
            path=f"/{self.prefix}/{{item_id}}",
            endpoint=self.get_item_endpoint(),
            methods=["GET"],
            summary=f"获取{self.prefix}详情",
            tags=self.tags,
            dependencies=dependencies,
        )
        
        # 创建
        self.router.add_api_route(
            path=f"/{self.prefix}",
            endpoint=self.create_item_endpoint(),
            methods=["POST"],
            summary=f"创建{self.prefix}",
            tags=self.tags,
            dependencies=dependencies,
        )
        
        # 更新
        self.router.add_api_route(
            path=f"/{self.prefix}/{{item_id}}",
            endpoint=self.update_item_endpoint(),
            methods=["PUT"],
            summary=f"更新{self.prefix}",
            tags=self.tags,
            dependencies=dependencies,
        )
        
        # 删除
        self.router.add_api_route(
            path=f"/{self.prefix}/{{item_id}}",
            endpoint=self.delete_item_endpoint(),
            methods=["DELETE"],
            summary=f"删除{self.prefix}",
            tags=self.tags,
            dependencies=dependencies,
        ) 