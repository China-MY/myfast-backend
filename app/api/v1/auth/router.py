from fastapi import APIRouter

from app.api.v1.auth import login, logout

router = APIRouter()
router.include_router(login.router, tags=["认证授权"])
router.include_router(logout.router, prefix="/logout", tags=["认证授权"]) 