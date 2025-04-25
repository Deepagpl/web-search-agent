"""
Research Manager module for coordinating web research tasks.
"""
import asyncio
from typing import Dict, List, Optional
import json
import ssl
import google.cloud.aiplatform as aiplatform
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import lru_cache
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    SERPER_API_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_SEARCH_RESULTS,
    REQUEST_TIMEOUT
)

class ResearchManager:
    def __init__(self):
        # Initialize Gemini client
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        except Exception as e:
            print(f"Error initializing Gemini: {str(e)}")
            self.model = None
        
        # Initialize search API (will be set based on settings)
        self.search_api = None

    def conduct_research(self, query: str, settings: Dict) -> Dict:
        """
        Main research workflow coordinating the entire research process.
        """
        try:
            print("\n=== Starting Research Process ===")
            
            # 1. Perform web search
            print("Step 1: Performing web search...")
            search_results = self._search_web(query, settings)
            print(f"Found {len(search_results)} search results")
            
            # 2. Extract content from search results
            print("\nStep 2: Extracting content...")
            extracted_content = self._extract_content(search_results)
            print(f"Extracted content from {len(extracted_content)} sources")
            
            # 3. Analyze content
            print("\nStep 3: Analyzing content...")
            analyzed_content = self._analyze_content(extracted_content, query)
            print("Content analysis complete")
            if analyzed_content:
                print("Analysis result structure:", analyzed_content.keys())
            
            # 4. Generate final report
            print("\nStep 4: Generating final report...")
            report = self._generate_report(analyzed_content, query)
            print("Report generation complete")
            if report:
                print("Report structure:", report.keys())
            
            return report
            
        except Exception as e:
            print("\n=== Research Error ===")
            print(f"Error during research: {str(e)}")
            import traceback
            print("Traceback:")
            traceback.print_exc()
            raise
    
    def _verify_api_connection(self) -> bool:
        """Verify API connection before making requests."""
        try:
            response = self.session.get(
                "https://google.serper.dev/search",
                timeout=5,
                verify=False
            )
            return response.status_code == 200
        except:
            return False

    @lru_cache(maxsize=100)
    def _cached_search(self, query: str, time_range: str) -> List[Dict]:
        """Cached search results to reduce API calls."""
        payload = {
            "q": query,
            "num": MAX_SEARCH_RESULTS
        }
        
        if time_range != "All time":
            payload["timeRange"] = time_range.lower()
        
        try:
            response = self.session.post(
                "https://google.serper.dev/search",
                json=payload,
                timeout=REQUEST_TIMEOUT,
                verify=False
            )
            response.raise_for_status()
            return response.json().get("organic", [])
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def _search_web(self, query: str, settings: Dict) -> List[Dict]:
        """Perform web search using selected API."""
        from utils.search_apis import get_search_api
        
        try:
            # Initialize search API if needed
            if not self.search_api or self.search_api.name != settings["search_api"]:
                self.search_api = get_search_api(settings["search_api"])
            
            # Perform search
            results = self.search_api.search(query, settings)
            
            if not results:
                print("Warning: No results found")
                return []
                
            print(f"Found {len(results)} results from {settings['search_api']} API")
            return results
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise

    def _extract_content(self, search_results: List[Dict]) -> List[Dict]:
        """Extract relevant content from search results."""
        return [{
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", ""),
            "position": result.get("position", 0)
        } for result in search_results]

    def _analyze_content(self, content: List[Dict], original_query: str) -> Dict:
        """Analyze content using Gemini if available, otherwise provide basic analysis."""
        if not content:
            return self._create_empty_analysis()

        # Try to use Gemini for analysis
        try:
            from utils.api_checker import check_gemini_api
            gemini_ok, _ = check_gemini_api()
            
            if gemini_ok and self.model:
                return self._analyze_with_gemini(content, original_query)
            else:
                print("Gemini API unavailable, using basic analysis")
                return self._analyze_basic(content, original_query)
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return self._analyze_basic(content, original_query)

    def _create_empty_analysis(self) -> Dict:
        """Create empty analysis structure."""
        return {
            "executive_summary": {
                "overview": "No content found to analyze",
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

    def _analyze_basic(self, content: List[Dict], query: str) -> Dict:
        """Provide basic analysis when Gemini is unavailable."""
        # Create basic summary
        summary = f"Basic analysis of {len(content)} sources about '{query}'"
        
        # Extract main themes from titles
        themes = []
        evidence = []
        for item in content:
            if item["title"] and len(themes) < 5:
                themes.append(item["title"])
            if item["snippet"]:
                evidence.append(item["snippet"])
        
        return {
            "executive_summary": {
                "overview": summary,
                "highlights": evidence[:5],  # Use top 5 snippets as highlights
                "conclusions": [
                    f"Found {len(content)} relevant sources",
                    "Basic analysis provided due to AI service unavailability"
                ]
            },
            "detailed_findings": {
                "themes": themes,
                "evidence": evidence,
                "opposing_views": []
            },
            "source_analysis": [{
                "url": item["url"],
                "reliability_score": 70,  # Default score
                "reasoning": "Basic credibility assessment"
            } for item in content],
            "context": {
                "historical": "",
                "current": "Analysis performed without AI assistance",
                "future": "",
                "impacts": []
            },
            "recommendations": {
                "actions": ["Try again later for AI-powered analysis"],
                "research": ["Review sources manually"],
                "risks": ["Limited analysis depth"],
                "strategy": ["Focus on source content review"]
            }
        }

    def _analyze_with_gemini(self, content: List[Dict], original_query: str) -> Dict:
        """Analyze content using Gemini AI."""
        content_text = "\n\n".join([
            f"Title: {item['title']}\nURL: {item['url']}\nContent: {item['snippet']}"
            for item in content
        ])

        try:
            response = self.model.generate_content(
                f"""Please analyze the provided content and present a comprehensive research report using the following structured format:

                RESEARCH TOPIC: {original_query}

                CONTENT TO ANALYZE:
                {content_text}

                Please provide your analysis in the following detailed structure:

                1. EXECUTIVE SUMMARY
                - Overview: Write a comprehensive 2-3 paragraph summary
                - Key Highlights: List 5-7 most important points
                - Main Conclusions: 2-3 primary takeaways

                2. DETAILED FINDINGS
                - Major Themes (3-5):
                  * Theme description
                  * Supporting evidence
                  * Statistical data if available
                - Opposing Viewpoints:
                  * Alternative perspectives
                  * Counter-arguments
                - Emerging Patterns:
                  * Trends
                  * Common elements

                3. SOURCE ANALYSIS
                For each source:
                - URL
                - Credibility Score (0-100)
                - Expertise Level
                - Publication Impact
                - Bias Assessment
                - Citation Analysis

                4. CONTEXTUAL ANALYSIS
                - Historical Background:
                  * Key developments
                  * Evolution of topic
                - Current Landscape:
                  * Present state
                  * Key stakeholders
                - Future Implications:
                  * Predicted trends
                  * Potential impacts

                5. RECOMMENDATIONS
                - Actionable Insights (3-5):
                  * Specific actions
                  * Implementation steps
                - Research Gaps:
                  * Areas needing further study
                  * Open questions
                - Risk Assessment:
                  * Potential challenges
                  * Mitigation strategies
                - Strategic Considerations:
                  * Long-term implications
                  * Success factors

                Format your response as a clear, professional research report with detailed explanations and evidence-based analysis.
                Present the information in a structured, easy-to-follow format with clear section headings.
                """,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40
                }
            )

            if not response.text:
                raise ValueError("Empty response from Gemini")

            # Parse and structure the response
            sections = {}
            current_section = None
            current_subsection = None
            buffer = []

            for line in response.text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Main sections
                if "1. EXECUTIVE SUMMARY" in line:
                    current_section = "executive_summary"
                    sections[current_section] = {"overview": "", "highlights": [], "conclusions": []}
                elif "2. DETAILED FINDINGS" in line:
                    current_section = "detailed_findings"
                    sections[current_section] = {"themes": [], "evidence": [], "opposing_views": [], "patterns": []}
                elif "3. SOURCE ANALYSIS" in line:
                    current_section = "source_analysis"
                    sections[current_section] = []
                elif "4. CONTEXTUAL ANALYSIS" in line:
                    current_section = "context"
                    sections[current_section] = {"historical": "", "current": "", "future": "", "impacts": []}
                elif "5. RECOMMENDATIONS" in line:
                    current_section = "recommendations"
                    sections[current_section] = {"actions": [], "research": [], "risks": [], "strategy": []}
                
                # Process content based on section
                elif current_section == "executive_summary":
                    if "Overview:" in line:
                        current_subsection = "overview"
                    elif "Key Highlights:" in line:
                        current_subsection = "highlights"
                    elif "Main Conclusions:" in line:
                        current_subsection = "conclusions"
                    elif line.startswith('*') or line.startswith('-'):
                        if current_subsection in ["highlights", "conclusions"]:
                            sections[current_section][current_subsection].append(line.strip('*- '))
                    elif current_subsection == "overview":
                        sections[current_section]["overview"] += line + " "
                
                elif current_section == "detailed_findings":
                    if "Major Themes" in line:
                        current_subsection = "themes"
                    elif "Supporting evidence" in line:
                        current_subsection = "evidence"
                    elif "Opposing Viewpoints" in line:
                        current_subsection = "opposing_views"
                    elif "Emerging Patterns" in line:
                        current_subsection = "patterns"
                    elif line.startswith('*') or line.startswith('-'):
                        if current_subsection:
                            sections[current_section][current_subsection].append(line.strip('*- '))
                
                elif current_section == "source_analysis":
                    if line.startswith('URL:'):
                        if buffer:
                            sections[current_section].append(dict(buffer))
                        buffer = []
                        buffer.append(("url", line.split(':', 1)[1].strip()))
                    elif line.startswith('Credibility Score:'):
                        buffer.append(("reliability_score", int(line.split(':', 1)[1].strip().rstrip('%'))))
                    elif line.startswith('Expertise Level:'):
                        buffer.append(("expertise", line.split(':', 1)[1].strip()))
                    elif line.startswith('Bias Assessment:'):
                        buffer.append(("reasoning", line.split(':', 1)[1].strip()))
                
                elif current_section == "context":
                    if "Historical Background:" in line:
                        current_subsection = "historical"
                    elif "Current Landscape:" in line:
                        current_subsection = "current"
                    elif "Future Implications:" in line:
                        current_subsection = "future"
                    elif line.startswith('*') or line.startswith('-'):
                        sections[current_section]["impacts"].append(line.strip('*- '))
                    elif current_subsection:
                        sections[current_section][current_subsection] += line + " "
                
                elif current_section == "recommendations":
                    if "Actionable Insights" in line:
                        current_subsection = "actions"
                    elif "Research Gaps" in line:
                        current_subsection = "research"
                    elif "Risk Assessment" in line:
                        current_subsection = "risks"
                    elif "Strategic Considerations" in line:
                        current_subsection = "strategy"
                    elif line.startswith('*') or line.startswith('-'):
                        if current_subsection:
                            sections[current_section][current_subsection].append(line.strip('*- '))

            # Add last source if any
            if current_section == "source_analysis" and buffer:
                sections["source_analysis"].append(dict(buffer))

            return sections

        except Exception as e:
            print(f"Analysis error: {str(e)}")
            raise

    def _generate_report(self, analysis: Dict, query: str) -> Dict:
        """Generate final research report with enhanced detail."""
        if not analysis:
            return {
                "query": query,
                "executive_summary": {
                    "overview": "Analysis failed or no content available",
                    "highlights": [],
                    "conclusions": []
                },
                "detailed_findings": {"themes": []},
                "source_analysis": [],
                "context": {"historical": "", "current": "", "future": ""},
                "recommendations": {"actions": [], "research": []}
            }

        return {
            "query": query,
            "executive_summary": analysis.get("executive_summary", {}),
            "detailed_findings": analysis.get("detailed_findings", {}),
            "source_analysis": analysis.get("source_analysis", []),
            "context": analysis.get("context", {}),
            "recommendations": analysis.get("recommendations", {})
        }
