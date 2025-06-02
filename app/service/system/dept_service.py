from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.system.dept import SysDept
from app.domain.models.system.role_dept import SysRoleDept
from app.domain.schemas.system.dept import DeptCreate, DeptUpdate, DeptInfo, DeptQuery
from app.common.exception import NotFound


def get_dept(db: Session, dept_id: int) -> Optional[SysDept]:
    """
    根据部门ID获取部门信息
    """
    return db.query(SysDept).filter(
        SysDept.dept_id == dept_id,
        SysDept.del_flag == "0"
    ).first()


def get_dept_by_name(db: Session, dept_name: str, parent_id: int = 0) -> Optional[SysDept]:
    """
    根据部门名称和父部门ID获取部门信息
    """
    return db.query(SysDept).filter(
        SysDept.dept_name == dept_name,
        SysDept.parent_id == parent_id,
        SysDept.del_flag == "0"
    ).first()


def get_depts(db: Session, params: DeptQuery) -> List[SysDept]:
    """
    获取部门列表
    """
    query = db.query(SysDept).filter(SysDept.del_flag == "0")
    
    # 构建查询条件
    if params.dept_name:
        query = query.filter(SysDept.dept_name.like(f"%{params.dept_name}%"))
    if params.status:
        query = query.filter(SysDept.status == params.status)
    
    # 按排序号升序
    depts = query.order_by(SysDept.parent_id.asc(), SysDept.order_num.asc()).all()
    
    return depts


def create_dept(db: Session, dept_data: DeptCreate) -> SysDept:
    """
    创建部门
    """
    # 检查部门名称是否已存在
    if get_dept_by_name(db, dept_data.dept_name, dept_data.parent_id):
        raise ValueError(f"同级部门下已存在: {dept_data.dept_name}")
    
    # 获取父部门信息
    parent_dept = None
    if dept_data.parent_id != 0:
        parent_dept = get_dept(db, dept_data.parent_id)
        if not parent_dept:
            raise ValueError(f"父部门不存在")
        
        # 如果父部门被禁用，则子部门也应该被禁用
        if parent_dept.status != "0":
            raise ValueError(f"父部门已停用，不允许新增")
    
    # 设置祖先字符串
    ancestors = "0" if dept_data.parent_id == 0 else (parent_dept.ancestors + "," + str(dept_data.parent_id))
    
    # 创建部门对象
    db_dept = SysDept(
        parent_id=dept_data.parent_id,
        ancestors=ancestors,
        dept_name=dept_data.dept_name,
        order_num=dept_data.order_num,
        leader=dept_data.leader,
        phone=dept_data.phone,
        email=dept_data.email,
        status=dept_data.status
    )
    
    # 保存部门信息
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    
    return db_dept


def update_dept(db: Session, dept_id: int, dept_data: DeptUpdate) -> Optional[SysDept]:
    """
    更新部门信息
    """
    # 获取部门信息
    db_dept = get_dept(db, dept_id)
    if not db_dept:
        raise NotFound(f"部门ID {dept_id} 不存在")
    
    # 不能将自己设为自己的父部门
    if dept_id == dept_data.parent_id:
        raise ValueError("父部门不能是自己")
    
    # 不能将自己设为自己的子部门的父部门
    if db_dept.parent_id != dept_data.parent_id:
        # 查找所有子部门
        children = db.query(SysDept).filter(
            SysDept.ancestors.like(f"%{dept_id}%"),
            SysDept.del_flag == "0"
        ).all()
        
        # 检查是否将自己设为子部门的父部门
        if any(child.dept_id == dept_data.parent_id for child in children):
            raise ValueError("父部门不能是自己的子部门")
    
    # 检查部门名称是否已存在（如果修改了部门名称或父部门）
    if (db_dept.dept_name != dept_data.dept_name or db_dept.parent_id != dept_data.parent_id) and \
       get_dept_by_name(db, dept_data.dept_name, dept_data.parent_id):
        raise ValueError(f"同级部门下已存在: {dept_data.dept_name}")
    
    # 如果修改了父部门，需要更新祖先字符串
    if db_dept.parent_id != dept_data.parent_id:
        # 获取新的父部门信息
        parent_dept = None
        if dept_data.parent_id != 0:
            parent_dept = get_dept(db, dept_data.parent_id)
            if not parent_dept:
                raise ValueError(f"父部门不存在")
            
            # 如果父部门被禁用，则子部门也应该被禁用
            if parent_dept.status != "0" and dept_data.status == "0":
                raise ValueError(f"父部门已停用，不允许启用")
        
        # 设置新的祖先字符串
        new_ancestors = "0" if dept_data.parent_id == 0 else (parent_dept.ancestors + "," + str(dept_data.parent_id))
        
        # 更新该部门的祖先字符串
        db_dept.ancestors = new_ancestors
        
        # 更新所有子部门的祖先字符串
        old_ancestors = db_dept.ancestors
        for child in children:
            child.ancestors = child.ancestors.replace(
                old_ancestors,
                new_ancestors
            )
    
    # 更新部门基本信息
    db_dept.parent_id = dept_data.parent_id
    db_dept.dept_name = dept_data.dept_name
    db_dept.order_num = dept_data.order_num
    db_dept.leader = dept_data.leader
    db_dept.phone = dept_data.phone
    db_dept.email = dept_data.email
    db_dept.status = dept_data.status
    
    # 提交事务
    db.commit()
    db.refresh(db_dept)
    
    return db_dept


def delete_dept(db: Session, dept_id: int) -> bool:
    """
    删除部门（逻辑删除）
    """
    # 获取部门信息
    db_dept = get_dept(db, dept_id)
    if not db_dept:
        raise NotFound(f"部门ID {dept_id} 不存在")
    
    # 检查是否有子部门
    has_children = db.query(SysDept).filter(
        SysDept.parent_id == dept_id,
        SysDept.del_flag == "0"
    ).first() is not None
    
    if has_children:
        raise ValueError(f"存在下级部门，不允许删除")
    
    # 检查部门下是否存在用户
    has_users = db.query("sys_user").filter(
        db.query("sys_user").c.dept_id == dept_id,
        db.query("sys_user").c.del_flag == "0"
    ).first() is not None
    
    if has_users:
        raise ValueError(f"部门存在用户，不允许删除")
    
    # 逻辑删除
    db_dept.del_flag = "2"
    db.commit()
    
    return True


def get_dept_tree(db: Session) -> List[Dict[str, Any]]:
    """
    获取部门树结构
    """
    # 获取所有正常状态的部门
    depts = db.query(SysDept).filter(
        SysDept.del_flag == "0"
    ).order_by(SysDept.parent_id.asc(), SysDept.order_num.asc()).all()
    
    # 按父ID分组
    dept_map = {}
    for dept in depts:
        if dept.parent_id not in dept_map:
            dept_map[dept.parent_id] = []
        dept_map[dept.parent_id].append(dept)
    
    # 递归构建树结构
    def build_tree(parent_id: int) -> List[Dict[str, Any]]:
        if parent_id not in dept_map:
            return []
        
        tree = []
        for dept in dept_map[parent_id]:
            node = {
                "id": dept.dept_id,
                "label": dept.dept_name,
                "children": build_tree(dept.dept_id)
            }
            tree.append(node)
        
        return tree
    
    # 从根节点开始构建
    return build_tree(0)


def build_dept_tree(depts: List[SysDept], parent_id: int = 0) -> List[Dict[str, Any]]:
    """
    构建部门树
    """
    tree = []
    for dept in depts:
        if dept.parent_id == parent_id:
            node = {
                "dept_id": dept.dept_id,
                "parent_id": dept.parent_id,
                "dept_name": dept.dept_name,
                "ancestors": dept.ancestors,
                "order_num": dept.order_num,
                "leader": dept.leader,
                "phone": dept.phone,
                "email": dept.email,
                "status": dept.status,
                "create_time": dept.create_time,
                "children": build_dept_tree(depts, dept.dept_id)
            }
            tree.append(node)
    return tree


def build_dept_tree_select(depts: List[SysDept], parent_id: int = 0) -> List[Dict[str, Any]]:
    """
    构建部门树选择项
    """
    tree = []
    for dept in depts:
        if dept.parent_id == parent_id:
            node = {
                "id": dept.dept_id,
                "label": dept.dept_name,
                "children": build_dept_tree_select(depts, dept.dept_id)
            }
            # 如果没有子节点，则移除children属性
            if not node["children"]:
                del node["children"]
            tree.append(node)
    return tree 