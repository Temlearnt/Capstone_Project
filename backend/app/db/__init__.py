# backend/app/db/__init__.py
"""Database module for Recruitly"""

from .supabase_client import get_supabase
from .operations import (
    test_connection,
    get_job_roles,
    create_company,
    get_company_by_id,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_last_login,
    create_screening_session,
    update_screening_status,
    get_screening_session,
    get_user_screening_sessions,
    save_candidates,
    get_candidates_by_screening
)

__all__ = [
    "get_supabase",
    "test_connection",
    "get_job_roles",
    "create_company",
    "get_company_by_id",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user_last_login",
    "create_screening_session",
    "update_screening_status",
    "get_screening_session",
    "get_user_screening_sessions",
    "save_candidates",
    "get_candidates_by_screening"
]