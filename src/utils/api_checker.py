"""
API status checking utilities.
"""
import requests
from typing import Dict, Tuple
import socket
from config import SERPER_API_KEY

def check_serper_api() -> Tuple[bool, str]:
    """Check if Serper API is accessible and working."""
    try:
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.get(
            "https://google.serper.dev/search",
            headers=headers,
            timeout=5,
            verify=False
        )
        if response.status_code == 200:
            return True, "Connected"
        else:
            return False, f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def check_gemini_api() -> Tuple[bool, str]:
    """Check if Gemini API is accessible."""
    try:
        # Try DNS resolution
        socket.gethostbyname("generativelanguage.googleapis.com")
        
        # Try connection
        socket.create_connection(
            ("generativelanguage.googleapis.com", 443),
            timeout=5
        )
        return True, "Connected"
    except socket.gaierror:
        return False, "DNS resolution failed"
    except socket.timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)

def get_api_status() -> Dict:
    """Get status of all APIs."""
    serper_ok, serper_msg = check_serper_api()
    gemini_ok, gemini_msg = check_gemini_api()
    
    return {
        "serper": {
            "status": "🟢 Online" if serper_ok else "🔴 Offline",
            "message": serper_msg
        },
        "gemini": {
            "status": "🟢 Online" if gemini_ok else "🔴 Offline",
            "message": gemini_msg
        }
    }
