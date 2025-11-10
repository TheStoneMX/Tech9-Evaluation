# Streamlit Web Interface Guide

## Overview

The Autonomous Research Assistant includes a beautiful, user-friendly web interface built with Streamlit. This provides a modern, interactive way to conduct AI-powered research.

## Features

### 🎨 Beautiful UI
- Modern gradient design
- Responsive layout
- Interactive components
- Real-time progress tracking

### 🔍 Research Capabilities
- Enter any research query
- Pre-built example queries
- Configurable settings
- Real-time status updates

### 📊 Rich Visualizations
- Quality metrics display
- Color-coded insights
- Categorized recommendations
- Source credibility ratings

### 💾 Export Options
- Download as JSON
- Download as Markdown
- Download as Plain Text
- One-click export

### 📜 Research History
- Automatic history tracking
- Quick access to past research
- Session persistence

---

## Quick Start

### 1. Setup (One Time)

```bash
cd 02_implementation
./setup.sh
```

Add your API keys to `.env`:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 2. Launch Web Interface

```bash
./run_streamlit.sh
```

Or directly:
```bash
streamlit run streamlit_app.py
```

The app will open automatically at: `http://localhost:8501`

---

## User Interface Guide

### Sidebar (Left)

**⚙️ Configuration**
- **Select Model**: Choose between GPT-4, GPT-3.5-turbo, Claude
- **Max Iterations**: Control research depth (1-5)
- **Search Depth**: Basic or Advanced search

**🔑 API Status**
- Visual indicators for API key status
- Quick validation before research

**📊 System Info**
- Architecture overview
- Framework information
- Current configuration

**📜 Research History**
- Last 5 research queries
- Click to reload previous reports
- Automatic tracking

### Main Area (Center)

**🔍 Research Query Section**
- Large text area for your query
- Example queries for quick start
- "Start Research" button
- Loading indicators

**🔄 Progress Tracking**
- Real-time status updates
- Progress bar visualization
- Step-by-step execution

**📄 Research Report**
- Executive summary
- Quality metrics (Coverage, Source Quality, Insight Depth)
- Strategic insights with confidence scores
- Actionable recommendations
- Source references with quality ratings
- Metadata and statistics

**💾 Export Section**
- Download JSON format
- Download Markdown format
- Download Plain Text format

---

## Using the Interface

### Step 1: Enter Your Research Query

In the text area, type your research question. Be specific for better results.

**Good Examples:**
```
✅ "AI agent frameworks market landscape and competitive analysis"
✅ "Electric vehicle adoption trends in European markets 2024-2025"
✅ "Enterprise SaaS pricing strategies in healthcare sector"
```

**Less Optimal:**
```
❌ "AI" (too broad)
❌ "Tell me about cars" (not specific enough)
```

### Step 2: Configure Settings (Optional)

In the sidebar, you can adjust:

- **Model**: GPT-4 (best quality) vs GPT-3.5-turbo (faster, cheaper)
- **Max Iterations**: Higher = more thorough but slower
- **Search Depth**: Advanced = better sources but more API calls

**Recommended Settings:**
- For quick research: GPT-3.5-turbo, 1-2 iterations, basic search
- For comprehensive research: GPT-4, 3 iterations, advanced search

### Step 3: Start Research

Click the **🚀 Start Research** button.

You'll see:
1. Progress bar with current step
2. Status messages
3. Estimated completion time (simulated)

**Note**: Button is disabled during research to prevent duplicate submissions.

### Step 4: Review Results

Once complete, the report appears with:

**📊 Quality Metrics**
- Coverage: How well topics were covered
- Source Quality: Average credibility of sources
- Insight Depth: Quality of analysis

**💡 Strategic Insights**
- Categorized by type (market trend, competitor analysis, opportunity, risk)
- Priority rating (1-5)
- Confidence score (0-100%)

**🎯 Recommendations**
- Actionable items
- Impact assessment (High/Medium/Low)
- Effort estimate (High/Medium/Low)
- Supporting rationale

**📚 Sources**
- Top sources with quality ratings (⭐⭐⭐⭐⭐)
- Clickable links to original sources
- Expandable list for all sources

### Step 5: Export Report

Choose your format:
- **JSON**: For programmatic use, integrations
- **Markdown**: For documentation, GitHub, blogs
- **TXT**: For simple text viewing, email

Files are automatically named with timestamp:
```
research_report_20250107_143025.json
research_report_20250107_143025.md
research_report_20250107_143025.txt
```

---

## Advanced Features

### Research History

The sidebar shows your last 5 research queries. Click any to reload that report instantly.

**Use Cases:**
- Compare different research angles
- Reference previous findings
- Build on past research

### Example Queries

Click any example query button to auto-populate and start research on:
- AI agent frameworks market landscape
- Electric vehicle market trends
- Quantum computing prospects
- Enterprise SaaS adoption

**Tip**: Modify example queries to match your specific needs!

### Real-Time Configuration

You can change settings between researches without restarting the app.

**Example Workflow:**
1. Run quick research with GPT-3.5, 1 iteration
2. Review results
3. Switch to GPT-4, 3 iterations for deeper analysis
4. Run same query again for comparison

---

## Troubleshooting

### App Won't Start

**Error**: `command not found: streamlit`

**Solution**:
```bash
pip install streamlit
# or
pip install -r requirements.txt
```

### API Key Errors

**Error**: Red indicators in sidebar

**Solution**:
1. Check `.env` file exists
2. Verify API keys are correct
3. Ensure no extra spaces or quotes
4. Restart Streamlit app

**Correct `.env` format:**
```
OPENAI_API_KEY=sk-proj-abc123...
TAVILY_API_KEY=tvly-xyz789...
```

### Research Fails

**Error**: "Research failed: ..."

**Common Causes:**
1. **Rate Limit**: Wait 1 minute, try again
2. **Invalid API Key**: Check credentials
3. **Network Issue**: Check internet connection
4. **Query Too Broad**: Make more specific

**Solutions:**
- Reduce max iterations
- Switch to basic search depth
- Make query more specific
- Check error message in app

### Slow Performance

**If research takes >5 minutes:**

1. Reduce max iterations (try 2 instead of 3)
2. Use basic search depth
3. Switch to GPT-3.5-turbo
4. Make query more focused

**Normal timing:**
- 1 iteration: 1-2 minutes
- 2 iterations: 2-4 minutes
- 3 iterations: 3-5 minutes

---

## Tips for Best Results

### Query Formulation

✅ **Do:**
- Be specific about industry, timeframe, geography
- Include key terms (market, analysis, trends, competitive)
- Specify what you want (landscape, forecast, comparison)

❌ **Don't:**
- Use single-word queries
- Ask yes/no questions
- Include unrelated topics in one query

### Settings Optimization

**For Exploration (Fast & Cheap):**
```
Model: GPT-3.5-turbo
Max Iterations: 1
Search Depth: Basic
Cost: ~$0.20, Time: ~1-2 min
```

**For Comprehensive Research:**
```
Model: GPT-4
Max Iterations: 3
Search Depth: Advanced
Cost: ~$0.60, Time: ~3-5 min
```

**For Balanced Research:**
```
Model: GPT-4
Max Iterations: 2
Search Depth: Advanced
Cost: ~$0.40, Time: ~2-3 min
```

### Iterative Research

1. Start with broad query (1 iteration)
2. Review initial insights
3. Refine query based on gaps
4. Run deeper research (3 iterations)
5. Export and synthesize

---

## Keyboard Shortcuts

Streamlit supports these shortcuts:

- `R`: Rerun the app
- `C`: Clear cache
- `?`: Show keyboard shortcuts
- `Ctrl+C`: Stop app (in terminal)

---

## Performance Benchmarks

**Typical Performance** (with Tavily API):

| Configuration | Time | Cost | Quality |
|--------------|------|------|---------|
| Fast (GPT-3.5, 1 iter) | 1-2 min | $0.20 | Good |
| Balanced (GPT-4, 2 iter) | 2-3 min | $0.40 | Great |
| Deep (GPT-4, 3 iter) | 3-5 min | $0.60 | Excellent |

**API Calls Per Research:**
- Iteration 1: 4-6 searches, 2-3 LLM calls
- Iteration 2: 3-4 searches, 2-3 LLM calls
- Iteration 3: 2-3 searches, 2 LLM calls

---

## Customization

### Changing Colors

Edit `streamlit_app.py` CSS section:

```python
# Find this section
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        # Change these hex colors
    }
</style>
""", unsafe_allow_html=True)
```

### Adding New Example Queries

Edit the `examples` list:

```python
examples = [
    "Your custom query 1",
    "Your custom query 2",
    "Your custom query 3",
    "Your custom query 4"
]
```

### Changing Default Settings

Modify the defaults in sidebar:

```python
max_iterations = st.slider(
    "Max Iterations",
    min_value=1,
    max_value=5,
    value=2,  # Change default here
)
```

---

## Security & Privacy

### API Keys
- Never commit `.env` file to Git
- Keys stored locally only
- Not transmitted except to official APIs

### Research Data
- Reports stored in session memory only
- Cleared when app restarts
- Not persisted to disk by default

### To Enable Persistence

Add to `streamlit_app.py`:

```python
import json
import os

# Save to file
def save_report(report):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{datetime.now().isoformat()}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
```

---

## FAQ

**Q: Can I run multiple researches in parallel?**
A: No, the app runs one research at a time. Start a new research after the previous completes.

**Q: Is my research history saved?**
A: Only during the current session. Restarting the app clears history.

**Q: Can I share reports with my team?**
A: Yes, use the export feature to download and share files.

**Q: Does it work offline?**
A: No, requires internet for API calls (OpenAI, Tavily).

**Q: Can I use my own API endpoints?**
A: Yes, modify the code to point to your endpoints.

**Q: Is there a mobile version?**
A: Streamlit is responsive but optimized for desktop/tablet.

---

## Next Steps

1. **Try the Interface**: Launch and run a sample research
2. **Explore Settings**: Test different configurations
3. **Export Reports**: Practice downloading in different formats
4. **Build History**: Run multiple researches to see history
5. **Customize**: Tweak colors, examples, defaults to your preferences

---

## Support

For issues or questions:
1. Check this guide
2. Review error messages in app
3. Check `.env` file configuration
4. Verify API keys are valid
5. Review main README.md

**Enjoy your AI-powered research assistant!** 🚀
