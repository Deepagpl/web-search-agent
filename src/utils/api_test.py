"""
API testing utilities for search services.
"""
import requests
from typing import Dict, Tuple
import streamlit as st
from config import SERPER_API_KEY, TAVILY_API_KEY, ERROR_MESSAGES

def test_serper_api() -> Dict[str, str]:
    """Test Serper API connectivity and functionality."""
    try:
        # Test basic connectivity
        response = requests.get(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            return {
                "status": "🔴 Offline",
                "message": f"API returned status code {response.status_code}"
            }

        # Test search functionality
        test_response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "q": "test query",
                "num": 1
            }
        )
        
        if test_response.status_code == 200 and test_response.json().get("organic"):
            return {
                "status": "🟢 Online",
                "message": "API is working correctly"
            }
        else:
            return {
                "status": "🟡 Limited",
                "message": "API responding but search may be restricted"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "🔴 Offline",
            "message": str(e)
        }

def test_tavily_api() -> Dict[str, str]:
    """Test Tavily API connectivity and functionality."""
    try:
        # Test health endpoint
        health_response = requests.get(
            "https://api.tavily.com/health",
            headers={
                "Authorization": f"Bearer {TAVILY_API_KEY}"
            },
            timeout=5
        )
        
        if health_response.status_code != 200:
            return {
                "status": "🔴 Offline",
                "message": f"Health check failed with status {health_response.status_code}"
            }

        # Test search functionality
        search_response = requests.get(
            "https://api.tavily.com/search",
            params={
                "api_key": TAVILY_API_KEY,
                "query": "test query",
                "max_results": 1,
                "include_images": False
            }
        )
        
        if search_response.status_code == 200 and search_response.json().get("results"):
            return {
                "status": "🟢 Online",
                "message": "API is working correctly"
            }
        else:
            return {
                "status": "🟡 Limited",
                "message": "API responding but search may be restricted"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "🔴 Offline",
            "message": str(e)
        }

@st.cache_data(ttl=300)  # Cache results for 5 minutes
def check_search_apis() -> Dict[str, Dict[str, str]]:
    """Check status of all search APIs."""
    return {
        "serper": test_serper_api(),
        "tavily": test_tavily_api()
    }

def display_api_status():
    """Display API status in Streamlit sidebar."""
    st.sidebar.header("🔌 Search API Status")
    
    if st.sidebar.button("🔄 Check API Status", use_container_width=True):
        with st.sidebar.status("Checking APIs..."):
            status = check_search_apis()
            
            # Display Serper status
            st.sidebar.subheader("Serper API")
            if "Online" in status["serper"]["status"]:
                st.sidebar.success(status["serper"]["status"])
            elif "Limited" in status["serper"]["status"]:
                st.sidebar.warning(status["serper"]["status"])
            else:
                st.sidebar.error(status["serper"]["status"])
            if "message" in status["serper"]:
                st.sidebar.info(status["serper"]["message"])
            
            # Display Tavily status
            st.sidebar.subheader("Tavily API")
            if "Online" in status["tavily"]["status"]:
                st.sidebar.success(status["tavily"]["status"])
            elif "Limited" in status["tavily"]["status"]:
                st.sidebar.warning(status["tavily"]["status"])
            else:
                st.sidebar.error(status["tavily"]["status"])
            if "message" in status["tavily"]:
                st.sidebar.info(status["tavily"]["message"])
            
            # Show recommendations if both APIs are down
            if "Offline" in status["serper"]["status"] and "Offline" in status["tavily"]["status"]:
                st.sidebar.error("⚠️ All search APIs are unavailable")
                st.sidebar.warning("""
                    Please check:
                    1. Your internet connection
                    2. API key configuration
                    3. Service status pages
                """)
    
    st.sidebar.divider()
