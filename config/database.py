from supabase import create_client, Client
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseConnection:
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            try:
                cls._client = create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=settings.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._client
    
    @classmethod
    def get_service_client(cls) -> Client:
        """Get Supabase client with service role key for admin operations"""
        try:
            return create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase service client: {e}")
            raise
    
    @classmethod
    def get_authenticated_client(cls, access_token: str) -> Client:
        """Get Supabase client with user authentication token"""
        try:
            # For now, let's just use the regular client and handle authentication at the request level
            # This is a simpler approach that should work with the current Supabase Python client
            client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
            
            # We'll add the Authorization header manually to storage requests
            return client
        except Exception as e:
            logger.error(f"Failed to create authenticated Supabase client: {e}")
            raise

# Convenience function to get the client
def get_supabase() -> Client:
    return SupabaseConnection.get_client()

def get_supabase_service() -> Client:
    return SupabaseConnection.get_service_client()

def get_supabase_authenticated(access_token: str) -> Client:
    return SupabaseConnection.get_authenticated_client(access_token)