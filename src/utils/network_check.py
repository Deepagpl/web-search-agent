"""
Network diagnostics and connection testing utilities.
"""
import socket
import subprocess
import platform
import requests
import ssl
from urllib3.util.retry import Retry
import json
from pathlib import Path
import sys
import warnings
from urllib3.exceptions import InsecureRequestWarning
from .warning_handler import suppress_warnings, handler

# Define warning categories
RESOURCE_WARNINGS = [Warning]  # Catch all resource-related warnings

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import SERPER_API_KEY

class NetworkDiagnostics:
    def __init__(self):
        self.target_host = "google.serper.dev"
        self.api_key = SERPER_API_KEY
        self.results = []
        
    def run_all_checks(self) -> list:
        """Run all network diagnostic checks."""
        self.check_dns()
        self.check_ping()
        self.check_ssl()
        self.test_api_variations()
        return self.results
        
    def check_dns(self):
        """Check DNS resolution."""
        try:
            ip = socket.gethostbyname(self.target_host)
            self.results.append(("DNS Resolution", "Success", f"Resolved to {ip}"))
        except socket.gaierror as e:
            self.results.append(("DNS Resolution", "Failed", f"DNS lookup failed: {str(e)}"))
            
    def check_ping(self):
        """Check if host responds to ping."""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", self.target_host]
        
        with suppress_warnings(RESOURCE_WARNINGS):
            try:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
                if "TTL=" in output or "ttl=" in output:
                    self.results.append(("Ping Test", "Success", "Host is responding to ping"))
                else:
                    self.results.append(("Ping Test", "Warning", "Host not responding to ping"))
            except subprocess.CalledProcessError:
                self.results.append(("Ping Test", "Failed", "Ping failed"))
            
    def check_ssl(self):
        """Test SSL connection with different configurations."""
        context = None
        try:
            # Try default SSL context
            context = ssl.create_default_context()
            with socket.create_connection((self.target_host, 443)) as sock:
                try:
                    with context.wrap_socket(sock, server_hostname=self.target_host) as ssock:
                        cipher = ssock.cipher()
                        self.results.append(("SSL Connection", "Success", f"Connected using {cipher[0]}"))
                except ssl.SSLError as e:
                    self.results.append(("SSL Connection", "Warning", f"Default SSL failed: {str(e)}"))
                    raise
        except Exception as e:
            self.results.append(("SSL Connection", "Warning", f"Default SSL failed: {str(e)}"))
            
            # Try without verification
            try:
                context = ssl._create_unverified_context()
                with socket.create_connection((self.target_host, 443)) as sock:
                    with context.wrap_socket(sock) as ssock:
                        self.results.append(("SSL Connection", "Warning", "Connected without verification"))
            except Exception as e:
                self.results.append(("SSL Connection", "Failed", f"All SSL attempts failed: {str(e)}"))
                
    def test_api_variations(self):
        """Test API connection with different configurations."""
        headers_variations = [
            {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            },
            {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        ]
        
        test_payload = {
            "q": "test query",
            "num": 1
        }
        
        # Configure session with retries
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))
        
        # Disable SSL verification warnings
        with suppress_warnings([InsecureRequestWarning]):
        
            # Test each header variation
            for i, headers in enumerate(headers_variations, 1):
                try:
                    response = session.post(
                        f"https://{self.target_host}/search",
                        headers=headers,
                        json=test_payload,
                        timeout=5,
                        verify=False  # Initially try without verification
                    )
                    
                    if response.status_code == 200:
                        self.results.append((
                            f"API Test {i}",
                            "Success",
                            f"Connected successfully with header variation {i}"
                        ))
                        return  # Found working configuration
                    else:
                        self.results.append((
                            f"API Test {i}",
                            "Warning",
                            f"Status code: {response.status_code}, Response: {response.text[:100]}"
                        ))
                except Exception as e:
                    self.results.append((
                        f"API Test {i}",
                        "Failed",
                        f"Connection failed: {str(e)}"
                    ))

def analyze_connection_issues(results: list) -> dict:
    """Analyze diagnostic results and provide recommendations."""
    analysis = {
        "status": "unknown",
        "issues": [],
        "recommendations": []
    }
    
    # Check for critical failures
    dns_failed = any(r[0] == "DNS Resolution" and r[1] == "Failed" for r in results)
    ssl_failed = any(r[0] == "SSL Connection" and r[1] == "Failed" for r in results)
    api_failed = all(r[0].startswith("API Test") and r[1] != "Success" for r in results)
    
    if dns_failed:
        analysis["issues"].append("DNS resolution failure")
        analysis["recommendations"].extend([
            "Check if the domain is accessible from your network",
            "Try using a different DNS server",
            "Check your network connectivity"
        ])
        
    if ssl_failed:
        analysis["issues"].append("SSL certificate verification failure")
        analysis["recommendations"].extend([
            "Update your SSL certificates",
            "Check if your system time is correct",
            "Try temporarily disabling SSL verification for testing"
        ])
        
    if api_failed:
        analysis["issues"].append("API connection failure")
        analysis["recommendations"].extend([
            "Verify your API key is correct",
            "Check if you've exceeded API rate limits",
            "Try using a VPN or different network"
        ])
        
    # Set overall status
    if not analysis["issues"]:
        analysis["status"] = "healthy"
    elif len(analysis["issues"]) > 2:
        analysis["status"] = "critical"
    else:
        analysis["status"] = "degraded"
        
    return analysis

def run_diagnostics() -> tuple[list, dict]:
    """Run network diagnostics and return results with analysis."""
    diagnostics = NetworkDiagnostics()
    results = diagnostics.run_all_checks()
    analysis = analyze_connection_issues(results)
    return results, analysis
