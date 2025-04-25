"""
Utility for handling and managing warnings.
"""
import warnings
from urllib3.exceptions import InsecureRequestWarning
import streamlit as st
from contextlib import contextmanager
from typing import List, Dict, Optional, Type

class WarningHandler:
    def __init__(self):
        self.warnings = []
        self.enabled = True
        
    def __call__(self, message, category, filename, lineno, file=None, line=None):
        """Handle warning as a callable."""
        if self.enabled:
            warning_info = {
                "message": str(message),
                "category": category.__name__,
                "file": filename,
                "line": lineno,
                "context": line
            }
            self.warnings.append(warning_info)
            
    def clear(self):
        """Clear stored warnings."""
        self.warnings = []
        
    def disable(self):
        """Disable warning collection."""
        self.enabled = False
        
    def enable(self):
        """Enable warning collection."""
        self.enabled = True
        
    def get_warnings(self) -> List[Dict]:
        """Get collected warnings."""
        return self.warnings

@contextmanager
def suppress_warnings(warning_types: Optional[List[Type[Warning]]] = None):
    """
    Context manager to suppress specific warnings.
    
    Args:
        warning_types: List of warning types to suppress. If None, suppresses all warnings.
    """
    with warnings.catch_warnings():
        if warning_types:
            for warning_type in warning_types:
                warnings.filterwarnings("ignore", category=warning_type)
        else:
            warnings.simplefilter("ignore")
        yield

def setup_warning_filters():
    """Setup default warning filters."""
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
def display_warnings_ui(handler: WarningHandler):
    """
    Display warnings in Streamlit UI.
    
    Args:
        handler: WarningHandler instance containing warnings.
    """
    warnings = handler.get_warnings()
    if warnings:
        st.sidebar.warning("⚠️ Non-critical issues detected")
        with st.sidebar.expander("View Warning Details"):
            for warning in warnings:
                message = warning["message"]
                category = warning["category"]
                
                if "SSL" in message or "certificate" in message.lower():
                    st.info(f"🔒 SSL Warning: {message}")
                elif "deprecation" in category.lower():
                    st.info(f"📢 Deprecation Notice: {message}")
                else:
                    st.info(f"ℹ️ {category}: {message}")
                    
            st.markdown("""
            **Common Solutions:**
            1. SSL Warnings: These are expected and safe to ignore for our use case
            2. Deprecation Notices: These don't affect functionality
            3. For other warnings, check the documentation or contact support
            """)

# Create global warning handler
handler = WarningHandler()

# Set up the warning handler
warnings.showwarning = handler
