from supabase import create_client, Client
from ..config import settings
import logging

logger = logging.getLogger(__name__)

_supabase_client: Client = None

def get_supabase() -> Client:
    """Get Supabase client instance (singleton)"""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("SUPABASE_URL or SUPABASE_KEY not set!")
            return None
        
        logger.info(f"Connecting to Supabase: {settings.SUPABASE_URL}")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized")
    
    return _supabase_client