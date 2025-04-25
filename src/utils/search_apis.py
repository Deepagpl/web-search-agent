"""
Search API implementations and handlers.
"""
import requests
import functools
from typing import Dict, List
from config import SEARCH_APIS, ERROR_MESSAGES, REQUEST_TIMEOUT

def handle_api_errors(func):
    """Decorator to handle API errors consistently."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "401" in str(e):
                raise Exception(ERROR_MESSAGES["api_unavailable"])
            elif "429" in str(e):
                raise Exception(ERROR_MESSAGES["rate_limit"])
            elif "timeout" in str(e):
                raise Exception(ERROR_MESSAGES["network_error"])
            else:
                raise Exception(f"Search failed: {str(e)}")
    return wrapper

class SerperAPI:
    """Serper API implementation."""
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        self.endpoint = SEARCH_APIS["serper"]["endpoint"]
    
    @handle_api_errors
    def search(self, query: str, settings: Dict) -> List[Dict]:
        """Perform search using Serper API."""
        params = {
            "q": query,
            "num": settings.get("max_results", 10)
        }
        
        time_range = settings.get("time_range", "All time")
        if time_range != "All time":
            params["timeRange"] = time_range.lower()
        
        response = self.session.post(
            self.endpoint,
            json=params,
            timeout=REQUEST_TIMEOUT,
            verify=False
        )
        response.raise_for_status()
        return response.json().get("organic", [])
    
    def check_status(self) -> Dict[str, str]:
        """Check API health."""
        try:
            response = self.session.get(
                self.endpoint,
                timeout=5,
                verify=False
            )
            if response.status_code == 200:
                return {
                    "status": "🟢 Online",
                    "message": "API is working"
                }
            else:
                return {
                    "status": "🔴 Offline",
                    "message": f"API returned status {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "🔴 Offline",
                "message": str(e)
            }

class TavilyAPI:
    """Tavily API implementation using official SDK."""
    def __init__(self, api_key: str):
        from tavily import TavilyClient
        self.client = TavilyClient(api_key=api_key)
        self.endpoint = SEARCH_APIS["tavily"]["endpoint"]
    
    @handle_api_errors
    def search(self, query: str, settings: Dict) -> List[Dict]:
        """Perform search using Tavily API."""
        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=settings.get("max_results", 10),
            include_images=False,
            include_answer=False
        )
        
        # Convert Tavily format to standard format
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "snippet": item.get("content", ""),
                "position": len(results) + 1
            })
        return results
    
    def check_status(self) -> Dict[str, str]:
        """Check API health."""
        try:
            # Try a minimal search to verify API
            response = self.client.search(
                "test",
                max_results=1,
                include_answer=False
            )
            if response and "results" in response:
                return {
                    "status": "🟢 Online",
                    "message": "API is working"
                }
            else:
                return {
                    "status": "🟡 Limited",
                    "message": "API responding but may be restricted"
                }
        except Exception as e:
            return {
                "status": "🔴 Offline",
                "message": str(e)
            }

def get_search_api(api_name: str):
    """Get configured search API instance."""
    if api_name == "serper":
        return SerperAPI(SEARCH_APIS["serper"]["key"])
    elif api_name == "tavily":
        return TavilyAPI(SEARCH_APIS["tavily"]["key"])
    else:
        raise ValueError(f"Unknown API: {api_name}")
