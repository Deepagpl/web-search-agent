# Web Research Agent 🔍

A powerful web research assistant that automates content discovery, analysis, and report generation using AI. This tool combines multiple search APIs with AI analysis to provide comprehensive research reports.

![Web Research Agent Demo](docs/images/demo.gif)

**Quick Example:**
```python
# Research about AI trends
query = "Latest developments in artificial intelligence 2025"
results = research_agent.conduct_research(
    query=query,
    settings={
        "search_api": "tavily",
        "max_results": 10,
        "time_range": "Month"
    }
)

# Get summarized insights
summary = results["executive_summary"]["overview"]
key_findings = results["detailed_findings"]["themes"]
```

## Table of Contents 📑
- [Features](#features-)
- [Installation](#installation-)
- [Usage Guide](#usage-guide-)
  - [Basic Research](#basic-research)
  - [Advanced Settings](#advanced-settings)
  - [View Options](#view-options)
- [Configuration](#configuration-)
  - [Required API Keys](#required-api-keys)
  - [Optional Settings](#optional-settings)
- [Architecture](#architecture-)
  - [Components](#components)
  - [Data Flow](#data-flow)
  - [Error Handling](#error-handling)
- [Contributing](#contributing-)
- [License](#license-)

## Features ✨

- **Multi-API Search Integration**
  - Serper API for Google search results
  - Tavily AI-powered search engine
  - Automatic fallback between APIs

- **AI-Powered Analysis**
  - Content summarization using Google's Gemini AI
  - Source credibility assessment
  - Key findings extraction
  - Context and recommendations

- **Flexible Display Options**
  - Enhanced View: Interactive research dashboard
  - Classic View: Traditional report format
  - Raw View: JSON data access

- **Advanced Features**
  - Real-time API status monitoring
  - Offline mode support
  - Customizable search depth
  - Source filtering
  - Time range selection

## Installation 🚀

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/web-research-agent.git
   cd web-research-agent
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   Create a `.env` file in the root directory:
   ```env
   SERPER_API_KEY=your_serper_api_key
   TAVILY_API_KEY=your_tavily_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Run the Application**
   ```bash
   streamlit run src/frontend/app.py
   ```

## Usage Guide 📖

### Basic Research
1. Enter your research query in the text area
2. Click "Start Research"
3. View results in your preferred format

### Advanced Settings
- **Search Depth**: Control research thoroughness (1-5)
- **Source Types**: Filter by News, Academic, Blogs, Forums
- **Time Range**: Filter by recency
- **Max Results**: Control number of sources (5-20)

### View Options
- **Enhanced View**
  - Interactive dashboard
  - Visual metrics
  - Expandable sections
  
- **Classic View**
  - Traditional report format
  - Source analysis
  - Key findings
  
- **Raw View**
  - JSON data access
  - Data download
  - Custom processing

## Configuration ⚙️

### Required API Keys
- **Serper API**: Get from [Serper.dev](https://serper.dev)
- **Tavily API**: Get from [Tavily AI](https://tavily.com)
- **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optional Settings
```python
# config.py
MAX_SEARCH_RESULTS = 10
DEFAULT_SEARCH_DEPTH = 3
REQUEST_TIMEOUT = 30
CACHE_ENABLED = True
```

## Architecture 🏗️

### Components
- **Frontend**: Streamlit-based user interface
- **Backend**: Research orchestration and analysis
- **Utils**: API integrations and helpers

### Data Flow
1. User Input → Search APIs
2. Content Extraction
3. AI Analysis
4. Report Generation
5. Display Results

### Error Handling
- API Fallbacks
- Offline Mode
- Graceful Degradation

## Contributing 🤝

### Setup Development Environment
1. Fork the repository
2. Create a feature branch
3. Set up pre-commit hooks

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints

### Testing
```bash
# Run tests
python -m pytest tests/
```

## License 📄

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
