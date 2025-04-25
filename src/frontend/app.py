import json
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.research_manager import ResearchManager
from utils.research_report import create_report_from_analysis, display_report
from config import MAX_SEARCH_RESULTS, DEFAULT_SEARCH_DEPTH

def initialize_session_state():
    """Initialize session state variables."""
    if 'research_results' not in st.session_state:
        st.session_state.research_results = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Web Research Agent",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .main {max-width: 1200px;}
        .stProgress > div > div > div > div {
            background-color: #1f77b4;
            background-image: linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent);
            background-size: 1rem 1rem;
        }
        .stAlert > div {padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;}
        .streamlit-expanderHeader {background-color: #f8f9fa; border-radius: 0.5rem; margin: 0.5rem 0;}
        .stTabs [data-baseweb="tab-list"] {gap: 2rem;}
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
        }
        h1, h2, h3 {color: #1f77b4; margin-bottom: 1rem;}
        a {color: #1f77b4; text-decoration: none;}
        a:hover {color: #0056b3; text-decoration: underline;}
        </style>
        """, unsafe_allow_html=True)

def get_domain_name(url: str) -> str:
    """Extract readable domain name from URL."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain.replace("www.", "").split('.')[0].title()

def display_api_status():
    """Display API connection status and diagnostics in sidebar."""
    from utils.api_test import display_api_status
    from utils.api_checker import get_api_status
    
    # Display search API status
    display_api_status()
    
    # Display Gemini API status
    st.sidebar.header("🤖 Analysis API Status")
    status = get_api_status()
    
    if "Online" in status["gemini"]["status"]:
        st.sidebar.success(status["gemini"]["status"])
    else:
        st.sidebar.error(status["gemini"]["status"])
        st.sidebar.warning(f"Issue: {status['gemini']['message']}")
        st.sidebar.info("""
            💡 When Gemini is offline:
            - Web search still works
            - Basic analysis will be provided
            - Try again later for AI analysis
        """)
    
    st.sidebar.divider()

def display_sidebar():
    """Display and handle sidebar controls."""
    st.sidebar.title("🔍 Search Settings")
    display_api_status()
    
    # Search API selector
    selected_api = st.sidebar.radio(
        "Search Engine",
        ["Serper", "Tavily"],
        help="Choose which search API to use",
        key="search_api"
    )
    
    with st.sidebar.expander("🛠️ Advanced Settings", expanded=False):
        settings = {
            "search_api": selected_api.lower(),
            "depth": st.slider(
                "Search Depth",
                min_value=1,
                max_value=5,
                value=DEFAULT_SEARCH_DEPTH,
                help="Higher depth means more thorough research but takes longer"
            ),
            "sources": st.multiselect(
                "Source Types",
                ["News", "Academic", "Blogs", "Forums"],
                default=["News", "Academic"],
                help="Select the types of sources to include in research"
            ),
            "time_range": st.select_slider(
                "Time Range",
                options=["24h", "Week", "Month", "Year", "All time"],
                value="Month",
                help="Filter results by publication date"
            ),
            "max_results": st.slider(
                "Max Results",
                min_value=5,
                max_value=20,
                value=MAX_SEARCH_RESULTS,
                help="Maximum number of search results to analyze"
            )
        }
    
    # Show API status
    try:
        from utils.search_apis import get_search_api
        api = get_search_api(settings["search_api"])
        status = api.check_status()
        
        if "Online" in status["status"]:
            st.sidebar.success(f"✅ {selected_api} API: Available")
        else:
            st.sidebar.error(f"❌ {selected_api} API: Unavailable")
            st.sidebar.info(f"Try switching to {'Tavily' if selected_api == 'Serper' else 'Serper'}")
    except Exception as e:
        st.sidebar.error(f"❌ {selected_api} API: Error checking status")
        st.sidebar.info(str(e))
    
    return settings

def display_search_interface():
    """Display the main search interface."""
    st.title("🔍 Web Research Agent")
    st.markdown("""
        Enter your research query below. The agent will search the web, analyze content,
        and compile a comprehensive report based on the most relevant sources.
    """)
    
    query = st.text_area(
        "Research Query",
        placeholder="Enter your research topic or question...",
        help="Be specific for better results"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        start_research = st.button("Start Research", type="primary", use_container_width=True)
    with col2:
        clear_results = st.button("Clear", type="secondary", use_container_width=True)
        
    return query, start_research, clear_results

def display_classic_view(report):
    """Display results in classic format."""
    # Executive Summary
    st.header("📈 Executive Summary", divider="blue")
    st.markdown(report.sections["executive_summary"]["overview"])
    
    with st.expander("Key Highlights", expanded=True):
        for highlight in report.sections["executive_summary"]["highlights"]:
            st.markdown(f"• {highlight}")
            
    if report.sections["executive_summary"]["conclusions"]:
        with st.expander("Main Conclusions"):
            for conclusion in report.sections["executive_summary"]["conclusions"]:
                st.markdown(f"🎯 {conclusion}")
    
    # Detailed Findings
    st.header("🔍 Key Findings", divider="blue")
    for theme in report.sections["detailed_findings"]["themes"]:
        with st.expander(theme):
            # Show evidence if available
            matching_evidence = [
                e for e in report.sections["detailed_findings"]["evidence"]
                if e.lower().startswith(theme.lower()) or theme.lower() in e.lower()
            ]
            if matching_evidence:
                st.markdown("**Supporting Evidence:**")
                for evidence in matching_evidence:
                    st.markdown(f"- {evidence}")
            
            # Show opposing views if available
            if report.sections["detailed_findings"]["opposing_views"]:
                st.markdown("**Alternative Perspectives:**")
                for view in report.sections["detailed_findings"]["opposing_views"]:
                    st.info(f"💭 {view}")
    
    # Source Analysis
    st.header("📚 Sources & Credibility", divider="blue")
    col1, col2 = st.columns([1, 2])
    with col1:
        reliable_sources = len([s for s in report.sections["source_analysis"]["credibility_scores"].values() if s >= 80])
        total_sources = len(report.sections["source_analysis"]["credibility_scores"])
        st.metric("Reliable Sources", f"{reliable_sources}/{total_sources}")
    
    for url, score in report.sections["source_analysis"]["credibility_scores"].items():
        with st.expander(f"Source: {get_domain_name(url)}"):
            st.progress(score / 100)
            st.markdown(f"**Reliability Score:** {score}%")
            st.markdown(f"**Expertise:** {report.sections['source_analysis']['expertise_levels'].get(url, 'N/A')}")
            st.markdown(f"🔗 [Visit Source]({url})")

def display_raw_view(results):
    """Display raw data in a structured format."""
    st.header("📊 Raw Research Data", divider="blue")
    
    # Add section selector
    sections = {
        "Executive Summary": "executive_summary",
        "Detailed Findings": "detailed_findings",
        "Source Analysis": "source_analysis",
        "Context": "context",
        "Recommendations": "recommendations"
    }
    
    selected_section = st.selectbox("Select Section to View", list(sections.keys()))
    
    # Display selected section
    with st.expander("View JSON Data", expanded=True):
        st.json(results.get(sections[selected_section], {}))
    
    # Add download option
    col1, col2 = st.columns([3, 1])
    with col2:
        download_data = json.dumps(results, indent=2)
        st.download_button(
            "📥 Download Full JSON",
            download_data,
            "research_results.json",
            "application/json"
        )

def display_results(results):
    """Display research results in a user-friendly format."""
    if not results:
        return

    try:
        # Create detailed report
        report = create_report_from_analysis(results)
        
        # Add result metadata
        st.sidebar.success("✅ Research Complete")
        
        # Show result stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Sources Found",
                len(report.sections["source_analysis"]["credibility_scores"])
            )
        with col2:
            st.metric(
                "Key Findings",
                len(report.sections["detailed_findings"]["themes"])
            )
        with col3:
            try:
                avg_reliability = sum(
                    report.sections["source_analysis"]["credibility_scores"].values()
                ) / len(report.sections["source_analysis"]["credibility_scores"])
                st.metric("Avg. Reliability", f"{avg_reliability:.0f}%")
            except:
                st.metric("Avg. Reliability", "N/A")
        
        # Display view type selector with info
        view_col1, view_col2 = st.columns([3, 1])
        with view_col1:
            view_type = st.radio(
                "Select View",
                ["Enhanced", "Classic", "Raw"],
                horizontal=True,
                key="view_type"
            )
        with view_col2:
            if st.button("🔄 Refresh Analysis"):
                st.rerun()
        
        # Show appropriate view
        if view_type == "Enhanced":
            display_report(report)
        elif view_type == "Classic":
            display_classic_view(report)
        else:
            display_raw_view(results)
            
    except Exception as e:
        st.error("⚠️ Error displaying results")
        
        with st.expander("Error Details"):
            st.error(str(e))
            
        st.warning("""
        💡 Showing basic results due to error. You can:
        1. Try refreshing the page
        2. Switch to a different view type
        3. Try a different search API
        """)
        
        # Show raw results as fallback
        with st.expander("View Raw Results"):
            st.json(results)

def main():
    """Main application function."""
    from utils.warning_handler import setup_warning_filters
    setup_warning_filters()
    
    initialize_session_state()
    setup_page_config()
    
    try:
        settings = display_sidebar()
        query, start_research, clear_results = display_search_interface()
        
        if clear_results:
            st.session_state.research_results = None
            st.rerun()
            
        if start_research and query:
            with st.spinner("Researching... This may take a few minutes."):
                research_manager = ResearchManager()
                results = research_manager.conduct_research(
                    query=query,
                    settings=settings
                )
                st.session_state.research_results = results
                st.session_state.search_history.append({
                    "query": query,
                    "timestamp": pd.Timestamp.now()
                })
        
        if st.session_state.research_results:
            display_results(st.session_state.research_results)
            
    except Exception as e:
        st.error("An error occurred during research")
        st.error(str(e))

if __name__ == "__main__":
    main()
