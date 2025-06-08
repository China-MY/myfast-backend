from typing import Any, Dict, Optional

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        # 生成表名（默认为类名小写）
        # 如果想自定义表名，可以在子类中覆盖此属性
        # 例如：__tablename__ = "sys_user"
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """将ORM对象转为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """从字典创建ORM对象"""
        return cls(**data) 