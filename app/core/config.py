import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "FastAPI"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    
    # 跨域设置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:8000", "http://localhost:3000", "http://localhost:8080"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "MyFastAPI Admin"
    PROJECT_DESCRIPTION: str = "企业级后台管理系统"
    PROJECT_VERSION: str = "0.1.0"
    
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DB: str = "myfast_admin"
    MYSQL_PORT: str = "3306"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_SERVER')}:{values.get('MYSQL_PORT')}/{values.get('MYSQL_DB')}"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # JWT配置
    JWT_SECRET_KEY: str = "myfast-admin-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    
    # 上传文件配置
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 