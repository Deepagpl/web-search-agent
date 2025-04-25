"""
Diagnostic tools for API connection issues.
"""
import requests
import socket
from urllib.parse import urlparse
import ssl
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import SERPER_API_KEY

class APIConnectionDiagnostics:
    def __init__(self):
        self.base_url = "https://google.serper.dev"
        self.api_key = SERPER_API_KEY
        self.results = []
        
    def run_all_checks(self) -> list:
        """Run all diagnostic checks."""
        self.check_dns()
        self.check_api_key()
        self.check_ssl()
        self.check_basic_connection()
        self.check_api_connection()
        return self.results
        
    def check_dns(self) -> bool:
        """Check if DNS resolution works."""
        try:
            domain = urlparse(self.base_url).netloc
            socket.gethostbyname(domain)
            self.results.append(("DNS Resolution", "Success", "Domain resolves correctly"))
            return True
        except socket.gaierror as e:
            self.results.append(("DNS Resolution", "Failed", f"Cannot resolve domain: {str(e)}"))
            return False
            
    def check_api_key(self) -> bool:
        """Validate API key format."""
        if not self.api_key:
            self.results.append(("API Key", "Failed", "API key is missing"))
            return False
        if len(self.api_key) < 10:
            self.results.append(("API Key", "Failed", "API key appears too short"))
            return False
            
        self.results.append(("API Key", "Success", "API key format appears valid"))
        return True
        
    def check_ssl(self) -> bool:
        """Check SSL connection."""
        try:
            # Try creating SSL context
            context = ssl.create_default_context()
            self.results.append(("SSL Configuration", "Success", "SSL context created successfully"))
            return True
        except ssl.SSLError as e:
            self.results.append(("SSL Configuration", "Failed", f"SSL Error: {str(e)}"))
            return False
            
    def check_basic_connection(self) -> bool:
        """Test basic HTTPS connection."""
        try:
            response = requests.get(
                self.base_url,
                timeout=5,
                verify=True
            )
            self.results.append(("Basic Connection", "Success", f"Server responded with status {response.status_code}"))
            return True
        except requests.exceptions.SSLError:
            self.results.append(("Basic Connection", "Warning", "SSL verification failed, trying without verification"))
            try:
                response = requests.get(
                    self.base_url,
                    timeout=5,
                    verify=False
                )
                self.results.append(("Basic Connection (No SSL)", "Success", "Connection works without SSL verification"))
                return True
            except Exception as e:
                self.results.append(("Basic Connection", "Failed", f"Connection failed even without SSL: {str(e)}"))
                return False
        except Exception as e:
            self.results.append(("Basic Connection", "Failed", f"Connection error: {str(e)}"))
            return False
            
    def check_api_connection(self) -> bool:
        """Test actual API endpoint."""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": "test query",
            "num": 1
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload,
                timeout=5,
                verify=True
            )
            
            if response.status_code == 200:
                self.results.append(("API Connection", "Success", "API responded successfully"))
                return True
            elif response.status_code == 401:
                self.results.append(("API Connection", "Failed", "Invalid API key"))
            elif response.status_code == 429:
                self.results.append(("API Connection", "Failed", "Rate limit exceeded"))
            else:
                self.results.append(("API Connection", "Failed", f"API returned status code {response.status_code}"))
            
            return False
            
        except Exception as e:
            self.results.append(("API Connection", "Failed", f"API request failed: {str(e)}"))
            return False
            
def run_diagnostics() -> list:
    """Run all API diagnostics and return results."""
    diagnostics = APIConnectionDiagnostics()
    return diagnostics.run_all_checks()
