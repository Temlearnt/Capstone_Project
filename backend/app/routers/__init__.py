# backend/app/routers/__init__.py
from .auth import router as auth_router
from .screen import router as screen_router
from .test_db import router as test_db_router
from .upload import router as upload_router
from .status import router as status_router
from .result import router as result_router
from .history import router as history_router
from .dashboard import router as dashboard_router
from .job_roles import router as job_roles_router
from .profile import router as profile_router
from .candidates import router as candidates_router


__all__ = [
    "auth_router",
    "screen_router", 
    "test_db_router",
    "upload_router",
    "status_router",
    "result_router",
    "history_router",
    "dashboard_router",
    "job_roles_router",
    "profile_router",
    "candidates_router"
]