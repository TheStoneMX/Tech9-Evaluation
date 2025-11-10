"""
Streamlit Web Interface for Autonomous Research Assistant
"""

import streamlit as st
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from main import AutonomousResearchAssistant

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Autonomous Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .insight-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .source-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'research_history' not in st.session_state:
        st.session_state.research_history = []
    if 'current_report' not in st.session_state:
        st.session_state.current_report = None
    if 'is_researching' not in st.session_state:
        st.session_state.is_researching = False


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Autonomous Research Assistant</h1>
        <p>Multi-Agent AI System for Market Research & Competitive Analysis</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and info"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Model selection
        model = st.selectbox(
            "Select Model",
            ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            index=0,
            help="Choose the LLM model for agents"
        )

        # Max iterations
        max_iterations = st.slider(
            "Max Iterations",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum research iterations"
        )

        # Search depth
        search_depth = st.selectbox(
            "Search Depth",
            ["basic", "advanced"],
            index=1,
            help="Tavily search depth"
        )

        st.markdown("---")

        # API Status
        st.markdown("### 🔑 API Status")

        openai_key = os.getenv("OPENAI_API_KEY", "")
        tavily_key = os.getenv("TAVILY_API_KEY", "")

        if openai_key and openai_key != "your_openai_api_key_here":
            st.success("✅ OpenAI API Key")
        else:
            st.error("❌ OpenAI API Key Missing")

        if tavily_key and tavily_key != "your_tavily_api_key_here":
            st.success("✅ Tavily API Key")
        else:
            st.error("❌ Tavily API Key Missing")

        st.markdown("---")

        # System Info
        st.markdown("### 📊 System Info")
        st.info(f"""
        **Agent Architecture**: 3 Agents
        **Framework**: LangGraph
        **Coordination**: State-based
        **Search API**: Tavily
        """)

        st.markdown("---")

        # Research History
        st.markdown("### 📜 Research History")
        if st.session_state.research_history:
            for idx, item in enumerate(reversed(st.session_state.research_history[-5:])):
                if st.button(f"📄 {item['query'][:30]}...", key=f"history_{idx}"):
                    st.session_state.current_report = item['report']
        else:
            st.caption("No research history yet")

        return {
            "model": model,
            "max_iterations": max_iterations,
            "search_depth": search_depth
        }


def render_query_input(config):
    """Render the query input section"""
    st.markdown("### 🔍 Research Query")

    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_area(
            "Enter your research question",
            placeholder="E.g., AI agent frameworks market landscape and competitive analysis",
            height=100,
            help="Describe what you want to research. Be specific for better results."
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button(
            "🚀 Start Research",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.is_researching
        )

    # Example queries
    st.markdown("**Example queries:**")
    examples = [
        "AI agent frameworks market landscape 2024-2025",
        "Electric vehicle market trends and competitive analysis",
        "Quantum computing commercialization prospects",
        "Enterprise SaaS adoption in healthcare sector"
    ]

    cols = st.columns(len(examples))
    for idx, (col, example) in enumerate(zip(cols, examples)):
        with col:
            if st.button(f"📌 {example[:20]}...", key=f"example_{idx}", use_container_width=True):
                query = example
                submit_button = True

    return query, submit_button


async def run_research(query, config):
    """Run the research asynchronously"""
    st.session_state.is_researching = True

    # Create placeholder for progress
    progress_container = st.container()

    with progress_container:
        st.markdown("### 🔄 Research in Progress")

        # Progress steps
        steps = [
            "🎯 Planning research strategy...",
            "🔍 Gathering information...",
            "📊 Analyzing findings...",
            "✅ Generating insights..."
        ]

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate progress (in real implementation, hook into agent callbacks)
        for idx, step in enumerate(steps):
            status_text.markdown(f"**{step}**")
            progress_bar.progress((idx + 1) / len(steps))

            if idx < len(steps) - 1:
                await asyncio.sleep(1)  # Simulated delay

        # Run actual research
        try:
            assistant = AutonomousResearchAssistant(model_name=config["model"])

            report = await assistant.research(
                query=query,
                requirements={
                    "max_iterations": config["max_iterations"],
                    "search_depth": config["search_depth"]
                }
            )

            # Store in session state
            st.session_state.current_report = report
            st.session_state.research_history.append({
                "query": query,
                "report": report,
                "timestamp": datetime.now().isoformat()
            })

            progress_bar.progress(100)
            status_text.markdown("**✅ Research Complete!**")

            st.success("✅ Research completed successfully!")

        except Exception as e:
            st.error(f"❌ Research failed: {str(e)}")
            st.exception(e)

        finally:
            st.session_state.is_researching = False


def render_report(report):
    """Render the research report"""
    if not report:
        st.info("👆 Enter a research query above to get started!")
        return

    st.markdown("---")
    st.markdown("## 📄 Research Report")

    # Summary Section
    st.markdown("### 📋 Executive Summary")
    st.markdown(f"""
    <div class="metric-card">
        <h4>{report.get('query', 'Research Query')}</h4>
        <p>{report.get('summary', 'No summary available')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Get metadata for later use
    metadata = report.get('metadata') or {}

    # Insights Section
    st.markdown("### 💡 Strategic Insights")

    insights = report.get('insights', [])

    if insights:
        for idx, insight in enumerate(insights, 1):
            category = insight.get('category', 'general').replace('_', ' ').title()
            description = insight.get('description', '')
            priority = insight.get('priority', 3)
            confidence = insight.get('confidence', 0)

            st.markdown(f"""
            <div class="insight-card">
                <h4>💎 Insight #{idx}: {category}</h4>
                <p style="font-size: 1.1em; margin: 1rem 0;">{description}</p>
                <div style="display: flex; gap: 2rem; font-size: 0.9em;">
                    <div>⭐ Priority: {priority}/5</div>
                    <div>📈 Confidence: {confidence*100:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No insights generated yet.")

    # Recommendations Section
    st.markdown("### 🎯 Actionable Recommendations")

    recommendations = report.get('recommendations', [])

    if recommendations:
        for idx, rec in enumerate(recommendations, 1):
            title = rec.get('title', 'Recommendation')
            description = rec.get('description', '')
            rationale = rec.get('rationale', '')
            impact = rec.get('impact', 'medium').upper()
            effort = rec.get('effort', 'medium').upper()

            # Color code impact
            impact_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            effort_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

            st.markdown(f"""
            <div class="recommendation-card">
                <h4>🎯 Recommendation #{idx}: {title}</h4>
                <p style="font-size: 1.1em; margin: 1rem 0;">{description}</p>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <strong>Rationale:</strong> {rationale}
                </div>
                <div style="display: flex; gap: 2rem; font-size: 0.9em;">
                    <div>{impact_color.get(impact, '⚪')} Impact: {impact}</div>
                    <div>{effort_color.get(effort, '⚪')} Effort: {effort}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recommendations generated yet.")

    # Sources Section
    st.markdown("### 📚 Sources")

    sources = report.get('sources', [])

    if sources:
        # Show top 10 sources
        for idx, source in enumerate(sources[:10], 1):
            title = source.get('title', 'Unknown')
            url = source.get('url', '#')
            quality = source.get('quality_score', 0)
            stars = "⭐" * int(quality * 5)

            st.markdown(f"""
            <div class="source-card">
                <strong>{idx}. [{stars}] {title}</strong><br>
                <a href="{url}" target="_blank" style="font-size: 0.9em; color: #667eea;">{url}</a>
            </div>
            """, unsafe_allow_html=True)

        if len(sources) > 10:
            with st.expander(f"📖 View all {len(sources)} sources"):
                for idx, source in enumerate(sources[10:], 11):
                    title = source.get('title', 'Unknown')
                    url = source.get('url', '#')
                    quality = source.get('quality_score', 0)
                    stars = "⭐" * int(quality * 5)
                    st.markdown(f"{idx}. [{stars}] [{title}]({url})")
    else:
        st.info("No sources available.")

    # Metadata Section
    with st.expander("🔍 View Metadata"):
        st.json(metadata)

    # Export Section
    st.markdown("### 💾 Export Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON export
        json_str = json.dumps(report, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    with col2:
        # Markdown export
        md_content = generate_markdown_report(report)
        st.download_button(
            label="📥 Download Markdown",
            data=md_content,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

    with col3:
        # Text export
        txt_content = generate_text_report(report)
        st.download_button(
            label="📥 Download TXT",
            data=txt_content,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def generate_markdown_report(report):
    """Generate markdown version of report"""
    metrics = report.get('quality_metrics') or {}

    md = f"""# Research Report

## Query
{report.get('query', '')}

## Summary
{report.get('summary', '')}

## Quality Metrics
- Coverage: {metrics.get('coverage_score', 0)*100:.0f}%
- Source Quality: {metrics.get('source_quality_score', 0)*100:.0f}%
- Insight Depth: {metrics.get('insight_depth_score', 0)*100:.0f}%

## Strategic Insights

"""

    for idx, insight in enumerate(report.get('insights', []), 1):
        md += f"""### {idx}. {insight.get('category', '').replace('_', ' ').title()}
**Priority**: {insight.get('priority', 0)}/5 | **Confidence**: {insight.get('confidence', 0)*100:.0f}%

{insight.get('description', '')}

"""

    md += "## Recommendations\n\n"

    for idx, rec in enumerate(report.get('recommendations', []), 1):
        md += f"""### {idx}. {rec.get('title', '')}
**Impact**: {rec.get('impact', '')} | **Effort**: {rec.get('effort', '')}

{rec.get('description', '')}

*Rationale*: {rec.get('rationale', '')}

"""

    md += "## Sources\n\n"

    for idx, source in enumerate(report.get('sources', []), 1):
        md += f"{idx}. [{source.get('title', '')}]({source.get('url', '')})\n"

    return md


def generate_text_report(report):
    """Generate plain text version of report"""
    metrics = report.get('quality_metrics') or {}

    txt = f"""
================================================================================
AUTONOMOUS RESEARCH ASSISTANT - RESEARCH REPORT
================================================================================

Query: {report.get('query', '')}

{report.get('summary', '')}

--------------------------------------------------------------------------------
QUALITY METRICS
--------------------------------------------------------------------------------
Coverage: {metrics.get('coverage_score', 0)*100:.0f}%
Source Quality: {metrics.get('source_quality_score', 0)*100:.0f}%
Insight Depth: {metrics.get('insight_depth_score', 0)*100:.0f}%

--------------------------------------------------------------------------------
STRATEGIC INSIGHTS
--------------------------------------------------------------------------------

"""

    for idx, insight in enumerate(report.get('insights', []), 1):
        txt += f"""{idx}. [{insight.get('category', '').upper()}] (Priority: {insight.get('priority', 0)}/5, Confidence: {insight.get('confidence', 0)*100:.0f}%)
   {insight.get('description', '')}

"""

    txt += """--------------------------------------------------------------------------------
RECOMMENDATIONS
--------------------------------------------------------------------------------

"""

    for idx, rec in enumerate(report.get('recommendations', []), 1):
        txt += f"""{idx}. {rec.get('title', '')}
   Impact: {rec.get('impact', '').upper()} | Effort: {rec.get('effort', '').upper()}

   {rec.get('description', '')}

   Rationale: {rec.get('rationale', '')}

"""

    txt += """--------------------------------------------------------------------------------
SOURCES
--------------------------------------------------------------------------------

"""

    for idx, source in enumerate(report.get('sources', []), 1):
        txt += f"{idx}. {source.get('title', '')}\n   {source.get('url', '')}\n\n"

    txt += "================================================================================"

    return txt


def main():
    """Main Streamlit app"""
    init_session_state()
    render_header()

    # Sidebar
    config = render_sidebar()

    # Main content
    query, submit_button = render_query_input(config)

    # Handle submission
    if submit_button and query and not st.session_state.is_researching:
        asyncio.run(run_research(query, config))
        st.rerun()

    # Display current report
    if st.session_state.current_report:
        render_report(st.session_state.current_report)


if __name__ == "__main__":
    main()
