"""
Configuration settings for the Web Research Agent.
"""
from decouple import config

# API Keys
SERPER_API_KEY = config('SERPER_API_KEY', default='2d00145c87cf3c95e94e9bf90703fbb50857c6db')
TAVILY_API_KEY = config('TAVILY_API_KEY', default='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')
GEMINI_API_KEY = config('GEMINI_API_KEY', default='AIzaSyBUU68IANZ7Fkf8fsKxC5hZmwRxkG-qT40')
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-2.0-flash')

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
MAX_SEARCH_RESULTS = config('MAX_SEARCH_RESULTS', default=10, cast=int)
DEFAULT_SEARCH_DEPTH = config('DEFAULT_SEARCH_DEPTH', default=3, cast=int)
REQUEST_TIMEOUT = config('REQUEST_TIMEOUT', default=30, cast=int)

# Cache Settings
CACHE_ENABLED = config('CACHE_ENABLED', default=True, cast=bool)
CACHE_TTL = config('CACHE_TTL', default=3600, cast=int)  # 1 hour

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = config('MAX_REQUESTS_PER_MINUTE', default=60, cast=int)

# Error Messages
ERROR_MESSAGES = {
    "api_unavailable": "The search API is currently unavailable. Please try again later.",
    "partial_results": "Showing partial results due to analysis service being unavailable.",
    "no_results": "No results found for your query. Please try different keywords.",
    "rate_limit": "Request limit reached. Please wait a moment before trying again.",
    "network_error": "Network connection error. Please check your internet connection."
}
