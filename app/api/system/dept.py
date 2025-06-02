from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.domain.models.system.user import SysUser
from app.domain.models.system.dept import SysDept
from app.domain.schemas.system.dept import DeptCreate, DeptUpdate, DeptInfo, DeptQuery
from app.common.response import success, error, page
from app.service.system.dept_service import (
    get_dept, get_depts, create_dept, update_dept, delete_dept, get_dept_tree
)

router = APIRouter()


@router.get("/list", summary="获取部门列表")
async def get_dept_list(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
    params: DeptQuery = Depends(),
):
    """
    获取部门列表
    """
    try:
        depts = get_depts(db, params)
        dept_list = [
            {
                "dept_id": dept.dept_id,
                "parent_id": dept.parent_id,
                "ancestors": dept.ancestors,
                "dept_name": dept.dept_name,
                "order_num": dept.order_num,
                "leader": dept.leader,
                "phone": dept.phone,
                "email": dept.email,
                "status": dept.status,
                "create_time": dept.create_time
            }
            for dept in depts
        ]
        return success(data=dept_list)
    except Exception as e:
        return error(msg=str(e))


@router.get("/treeselect", summary="获取部门树选择数据")
async def get_dept_tree_select(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取部门树选择数据
    """
    try:
        dept_tree = get_dept_tree(db)
        return success(data=dept_tree)
    except Exception as e:
        return error(msg=str(e))


@router.get("/info/{dept_id}", summary="获取部门详情")
async def get_dept_info(
    dept_id: int = Path(..., description="部门ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    获取部门详情
    """
    try:
        dept = get_dept(db, dept_id)
        if not dept:
            return error(msg="部门不存在", code=404)
        dept_info = {
            "dept_id": dept.dept_id,
            "parent_id": dept.parent_id,
            "ancestors": dept.ancestors,
            "dept_name": dept.dept_name,
            "order_num": dept.order_num,
            "leader": dept.leader,
            "phone": dept.phone,
            "email": dept.email,
            "status": dept.status,
            "create_time": dept.create_time
        }
        return success(data=dept_info)
    except Exception as e:
        return error(msg=str(e))


@router.post("/add", summary="添加部门")
async def add_dept(
    dept_data: DeptCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    添加部门
    """
    try:
        dept = create_dept(db, dept_data)
        return success(msg="部门添加成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except Exception as e:
        return error(msg=str(e))


@router.put("/edit", summary="修改部门")
async def edit_dept(
    dept_data: DeptUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    修改部门
    """
    try:
        dept = update_dept(db, dept_data.dept_id, dept_data)
        return success(msg="部门修改成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e))


@router.delete("/remove/{dept_id}", summary="删除部门")
async def remove_dept(
    dept_id: int = Path(..., description="部门ID"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user),
):
    """
    删除部门
    """
    try:
        result = delete_dept(db, dept_id)
        return success(msg="部门删除成功")
    except ValueError as e:
        return error(msg=str(e), code=400)
    except HTTPException as e:
        return error(msg=e.detail, code=e.status_code)
    except Exception as e:
        return error(msg=str(e)) 