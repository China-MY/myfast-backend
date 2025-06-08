from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permissions
from app.models.user import SysUser
from app.models.dept import SysDept
from app.schemas.dept import DeptCreate, DeptUpdate, DeptOut, DeptTree
from app.schemas.common import ResponseModel
from app.crud.dept import dept as dept_crud

router = APIRouter()


@router.get("", response_model=ResponseModel[List[DeptOut]], summary="获取部门列表", description="获取所有部门列表")
def list_depts(
    db: Session = Depends(get_db),
    *,
    dept_name: Optional[str] = None,
    status: Optional[str] = None,
    _: bool = Depends(check_permissions(["system:dept:list"]))
) -> Any:
    """
    获取部门列表
    """
    depts = dept_crud.get_all_with_filter(
        db, 
        dept_name=dept_name,
        status=status
    )
    
    return ResponseModel[List[DeptOut]](data=depts)


@router.get("/tree", response_model=ResponseModel[List[DeptTree]], summary="获取部门树", description="获取部门树结构")
def get_dept_tree(
    db: Session = Depends(get_db),
    _: bool = Depends(check_permissions(["system:dept:list"]))
) -> Any:
    """
    获取部门树结构
    """
    depts = dept_crud.get_tree(db)
    return ResponseModel[List[DeptTree]](data=depts)


@router.get("/{dept_id}", response_model=ResponseModel[DeptOut], summary="获取部门详情", description="根据部门ID获取部门详情")
def get_dept(
    *,
    db: Session = Depends(get_db),
    dept_id: int,
    _: bool = Depends(check_permissions(["system:dept:query"]))
) -> Any:
    """
    获取部门详情
    """
    dept_obj = dept_crud.get_by_id(db, dept_id=dept_id)
    if not dept_obj:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    return ResponseModel[DeptOut](data=dept_obj)


@router.post("", response_model=ResponseModel[DeptOut], summary="创建部门", description="创建新部门")
def create_dept(
    *,
    db: Session = Depends(get_db),
    dept_in: DeptCreate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dept:add"]))
) -> Any:
    """
    创建新部门
    """
    # 检查父部门是否存在
    if dept_in.parent_id and dept_in.parent_id != 0:
        parent = dept_crud.get_by_id(db, dept_id=dept_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父部门不存在")
    
    # 检查部门名称是否重复
    if dept_crud.get_by_name(db, dept_name=dept_in.dept_name, parent_id=dept_in.parent_id):
        raise HTTPException(status_code=400, detail="同一层级下部门名称已存在")
    
    dept_obj = dept_crud.create(db, obj_in=dept_in, creator_id=current_user.user_id)
    return ResponseModel[DeptOut](data=dept_obj, msg="创建成功")


@router.put("/{dept_id}", response_model=ResponseModel[DeptOut], summary="更新部门", description="更新部门信息")
def update_dept(
    *,
    db: Session = Depends(get_db),
    dept_id: int,
    dept_in: DeptUpdate,
    current_user: SysUser = Depends(get_current_active_user),
    _: bool = Depends(check_permissions(["system:dept:edit"]))
) -> Any:
    """
    更新部门信息
    """
    dept_obj = dept_crud.get_by_id(db, dept_id=dept_id)
    if not dept_obj:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    # 检查父部门是否存在
    if dept_in.parent_id and dept_in.parent_id != 0:
        parent = dept_crud.get_by_id(db, dept_id=dept_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父部门不存在")
        
        # 不能将自己设为自己的父部门
        if dept_in.parent_id == dept_id:
            raise HTTPException(status_code=400, detail="不能选择自己作为父部门")
        
        # 不能将自己的子部门设为自己的父部门
        if dept_crud.is_child(db, parent_id=dept_id, child_id=dept_in.parent_id):
            raise HTTPException(status_code=400, detail="不能选择子部门作为父部门")
    
    # 检查部门名称是否重复
    if dept_in.dept_name and dept_in.dept_name != dept_obj.dept_name:
        parent_id = dept_in.parent_id if dept_in.parent_id is not None else dept_obj.parent_id
        if dept_crud.get_by_name(db, dept_name=dept_in.dept_name, parent_id=parent_id):
            raise HTTPException(status_code=400, detail="同一层级下部门名称已存在")
    
    dept_obj = dept_crud.update(db, db_obj=dept_obj, obj_in=dept_in, updater_id=current_user.user_id)
    return ResponseModel[DeptOut](data=dept_obj, msg="更新成功")


@router.delete("/{dept_id}", response_model=ResponseModel, summary="删除部门", description="删除指定部门")
def delete_dept(
    *,
    db: Session = Depends(get_db),
    dept_id: int,
    _: bool = Depends(check_permissions(["system:dept:remove"]))
) -> Any:
    """
    删除部门
    """
    dept_obj = dept_crud.get_by_id(db, dept_id=dept_id)
    if not dept_obj:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    # 检查是否有子部门
    if dept_crud.has_children(db, dept_id=dept_id):
        raise HTTPException(status_code=400, detail="存在子部门，不能删除")
    
    # 检查部门下是否有用户
    if dept_crud.has_users(db, dept_id=dept_id):
        raise HTTPException(status_code=400, detail="部门下存在用户，不能删除")
    
    dept_crud.remove(db, dept_id=dept_id)
    return ResponseModel(msg="删除成功")


@router.get("/select/options", response_model=ResponseModel[List[DeptTree]], summary="获取部门选项", description="获取部门树形选项")
def get_dept_options(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_active_user)
) -> Any:
    """
    获取部门树形选项
    """
    depts = dept_crud.get_tree(db, status="0")  # 只获取正常状态的部门
    return ResponseModel[List[DeptTree]](data=depts) 