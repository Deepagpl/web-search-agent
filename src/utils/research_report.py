"""
Enhanced research report generation and formatting.
"""
from typing import Dict, List, Any
from datetime import datetime
import streamlit as st

class ResearchReport:
    def __init__(self):
        self.sections = {
            "executive_summary": {
                "overview": "",
                "highlights": [],
                "conclusions": []
            },
            "detailed_findings": {
                "themes": [],
                "evidence": [],
                "opposing_views": [],
                "metrics": {}
            },
            "source_analysis": {
                "credibility_scores": {},
                "publication_dates": {},
                "expertise_levels": {},
                "citation_counts": {}
            },
            "context": {
                "historical": "",
                "current": "",
                "future": "",
                "industry_impact": []
            },
            "recommendations": {
                "actions": [],
                "further_research": [],
                "risks": [],
                "strategy": []
            }
        }

    def set_executive_summary(self, summary: str, highlights: List[str], conclusions: List[str]):
        """Set executive summary section."""
        self.sections["executive_summary"].update({
            "overview": summary,
            "highlights": highlights,
            "conclusions": conclusions
        })

    def add_detailed_finding(self, theme: str, evidence: List[str], opposing_view: str = None):
        """Add a detailed finding with supporting evidence."""
        self.sections["detailed_findings"]["themes"].append(theme)
        self.sections["detailed_findings"]["evidence"].extend(evidence)
        if opposing_view:
            self.sections["detailed_findings"]["opposing_views"].append(opposing_view)

    def add_source(self, url: str, credibility: int, expertise: str, citations: int = 0):
        """Add source analysis information."""
        self.sections["source_analysis"]["credibility_scores"][url] = credibility
        self.sections["source_analysis"]["expertise_levels"][url] = expertise
        self.sections["source_analysis"]["citation_counts"][url] = citations
        self.sections["source_analysis"]["publication_dates"][url] = datetime.now().strftime("%Y-%m-%d")

    def set_context(self, historical: str, current: str, future: str, impacts: List[str]):
        """Set contextual analysis."""
        self.sections["context"].update({
            "historical": historical,
            "current": current,
            "future": future,
            "industry_impact": impacts
        })

    def add_recommendations(self, actions: List[str], research: List[str], risks: List[str], strategy: List[str]):
        """Add recommendations section."""
        self.sections["recommendations"].update({
            "actions": actions,
            "further_research": research,
            "risks": risks,
            "strategy": strategy
        })

def display_report(report: ResearchReport):
    """Display the research report in a structured format."""
    # Executive Summary Section
    st.header("📊 Executive Summary", divider="blue")
    with st.expander("Overview", expanded=True):
        st.write(report.sections["executive_summary"]["overview"])
        
        st.subheader("Key Highlights")
        for highlight in report.sections["executive_summary"]["highlights"]:
            st.markdown(f"• {highlight}")
            
        st.subheader("Main Conclusions")
        for conclusion in report.sections["executive_summary"]["conclusions"]:
            st.markdown(f"🎯 {conclusion}")
    
    # Detailed Findings Section
    st.header("🔍 Detailed Analysis", divider="blue")
    themes_tab, evidence_tab, opposing_tab = st.tabs([
        "Major Themes", "Supporting Evidence", "Alternative Views"
    ])
    
    with themes_tab:
        for theme in report.sections["detailed_findings"]["themes"]:
            with st.container():
                st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
                        <h4>{theme}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
    with evidence_tab:
        for evidence in report.sections["detailed_findings"]["evidence"]:
            st.markdown(f"📝 {evidence}")
            
    with opposing_tab:
        for view in report.sections["detailed_findings"]["opposing_views"]:
            st.info(f"💭 {view}")
    
    # Source Analysis Section
    st.header("📚 Source Credibility Analysis", divider="blue")
    sources = report.sections["source_analysis"]
    
    for url in sources["credibility_scores"].keys():
        with st.expander(f"Source: {url}"):
            cols = st.columns([1, 2, 1])
            with cols[0]:
                st.metric("Credibility Score", f"{sources['credibility_scores'][url]}%")
            with cols[1]:
                st.write(f"Expertise: {sources['expertise_levels'][url]}")
            with cols[2]:
                st.write(f"Citations: {sources['citation_counts'][url]}")
                
    # Context Section
    st.header("🌐 Context & Implications", divider="blue")
    context = report.sections["context"]
    
    with st.expander("Historical Context"):
        st.write(context["historical"])
    with st.expander("Current Landscape"):
        st.write(context["current"])
    with st.expander("Future Outlook"):
        st.write(context["future"])
        
    st.subheader("Industry Impact")
    for impact in context["industry_impact"]:
        st.warning(impact)
    
    # Recommendations Section
    st.header("💡 Recommendations & Next Steps", divider="blue")
    recs = report.sections["recommendations"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Actionable Steps")
        for action in recs["actions"]:
            st.success(f"✅ {action}")
            
        st.subheader("Further Research")
        for research in recs["further_research"]:
            st.info(f"🔍 {research}")
            
    with col2:
        st.subheader("Potential Risks")
        for risk in recs["risks"]:
            st.error(f"⚠️ {risk}")
            
        st.subheader("Strategic Considerations")
        for strategy in recs["strategy"]:
            st.warning(f"🎯 {strategy}")

def validate_response(response: Dict) -> Dict:
    """Validate and normalize response format."""
    required_fields = {
        "executive_summary": {
            "overview": "",
            "highlights": [],
            "conclusions": []
        },
        "detailed_findings": {
            "themes": [],
            "evidence": [],
            "opposing_views": []
        },
        "source_analysis": [],
        "context": {
            "historical": "",
            "current": "",
            "future": "",
            "impacts": []
        },
        "recommendations": {
            "actions": [],
            "research": [],
            "risks": [],
            "strategy": []
        }
    }
    
    # Ensure all required fields exist
    validated = {}
    for section, defaults in required_fields.items():
        if section not in response:
            validated[section] = defaults
        else:
            if isinstance(defaults, dict):
                validated[section] = {
                    field: response[section].get(field, default)
                    for field, default in defaults.items()
                }
            else:
                validated[section] = response[section]
    
    return validated

def create_report_from_analysis(analysis: Dict[str, Any]) -> ResearchReport:
    """Create a detailed report from analysis results."""
    report = ResearchReport()
    
    # Handle both old and new format
    if isinstance(analysis.get("summary"), str) or isinstance(analysis.get("key_findings"), list):
        # Old format - convert to new format
        old_format = {
            "executive_summary": {
                "overview": analysis.get("summary", ""),
                "highlights": analysis.get("key_findings", []),
                "conclusions": analysis.get("key_findings", [])[-2:] if analysis.get("key_findings") else []
            },
            "detailed_findings": {
                "themes": analysis.get("key_findings", []),
                "evidence": [],
                "opposing_views": []
            },
            "source_analysis": [
                {
                    "url": s.get("url", ""),
                    "reliability_score": s.get("reliability", 0),
                    "reasoning": s.get("notes", "No analysis available")
                }
                for s in analysis.get("sources", [])
            ],
            "context": {
                "historical": "",
                "current": "",
                "future": "",
                "impacts": []
            },
            "recommendations": {
                "actions": [],
                "research": [],
                "risks": [],
                "strategy": []
            }
        }
        validated = validate_response(old_format)
    else:
        # New format - validate
        validated = validate_response(analysis)
    
    # Set executive summary
    report.set_executive_summary(
        summary=validated["executive_summary"]["overview"],
        highlights=validated["executive_summary"]["highlights"],
        conclusions=validated["executive_summary"]["conclusions"]
    )
    
    # Add detailed findings
    for theme in validated["detailed_findings"]["themes"]:
        report.add_detailed_finding(
            theme=theme,
            evidence=[e for e in validated["detailed_findings"]["evidence"] if e],
            opposing_view=validated["detailed_findings"]["opposing_views"][0] if validated["detailed_findings"]["opposing_views"] else None
        )
    
    # Add source analysis
    for source in validated["source_analysis"]:
        report.add_source(
            url=source.get("url", ""),
            credibility=source.get("reliability_score", 0),
            expertise=source.get("reasoning", "No expertise information available"),
            citations=source.get("citations", 0)
        )
    
    # Set context
    report.set_context(
        historical=validated["context"]["historical"],
        current=validated["context"]["current"],
        future=validated["context"]["future"],
        impacts=validated["context"]["impacts"]
    )
    
    # Add recommendations
    report.add_recommendations(
        actions=validated["recommendations"]["actions"],
        research=validated["recommendations"]["research"],
        risks=validated["recommendations"]["risks"],
        strategy=validated["recommendations"]["strategy"]
    )
    
    return report
