"""Service modules for FastAPI Generator."""
from .vercel import setup_vercel, remove_vercel
from .google_oauth import setup_google_oauth, remove_google_oauth

__all__ = [
    'setup_vercel', 
    'remove_vercel',
    'setup_google_oauth',
    'remove_google_oauth',
]
