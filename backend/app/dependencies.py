from .config import settings
from .db.supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)

async def get_db():
    """Dependency untuk mendapatkan Supabase client"""
    return get_supabase()

def init_mlflow():
    """Initialize MLflow tracking"""
    import mlflow
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    logger.info(f"MLflow tracking URI: {settings.MLFLOW_TRACKING_URI}")
    return mlflow