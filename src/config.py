"""
Configuration settings for the Web Research Agent.
"""
import os
from decouple import config

# Environment
IS_PRODUCTION = os.environ.get('DYNO') is not None  # Check if running on Heroku

# API Keys - try environment variables first (for Heroku), then fallback to .env
SERPER_API_KEY = os.environ.get('SERPER_API_KEY') or config('SERPER_API_KEY', default='')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY') or config('TAVILY_API_KEY', default='')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or config('GEMINI_API_KEY', default='')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL') or config('GEMINI_MODEL', default='gemini-2.0-flash')

# Search API Configuration
SEARCH_APIS = {
    "serper": {
        "endpoint": "https://google.serper.dev/search",
        "key": SERPER_API_KEY
    },
    "tavily": {
        "endpoint": "https://api.tavily.com/search",
        "key": TAVILY_API_KEY
    }
}

# Search Settings
MAX_SEARCH_RESULTS = int(os.environ.get('MAX_SEARCH_RESULTS') or config('MAX_SEARCH_RESULTS', default=10))
DEFAULT_SEARCH_DEPTH = int(os.environ.get('DEFAULT_SEARCH_DEPTH') or config('DEFAULT_SEARCH_DEPTH', default=3))
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT') or config('REQUEST_TIMEOUT', default=30))

# Cache Settings
CACHE_ENABLED = bool(os.environ.get('CACHE_ENABLED') or config('CACHE_ENABLED', default=True, cast=bool))
CACHE_TTL = int(os.environ.get('CACHE_TTL') or config('CACHE_TTL', default=3600))  # 1 hour

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = int(os.environ.get('MAX_REQUESTS_PER_MINUTE') or config('MAX_REQUESTS_PER_MINUTE', default=60))

# Error Messages
ERROR_MESSAGES = {
    "api_unavailable": "The search API is currently unavailable. Please try again later.",
    "partial_results": "Showing partial results due to analysis service being unavailable.",
    "no_results": "No results found for your query. Please try different keywords.",
    "rate_limit": "Request limit reached. Please wait a moment before trying again.",
    "network_error": "Network connection error. Please check your internet connection."
}
