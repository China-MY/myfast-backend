# 导入所有模型，确保它们在Base.metadata中注册
from app.db.base_class import Base
from app.domain.models.user import User 