# Demonstration Scenario

## Scenario Overview

**Use Case**: A consulting firm has been approached by a venture capital firm interested in the AI agent frameworks market. They need a comprehensive market analysis to inform their investment strategy.

**Research Query**: "AI agent frameworks market landscape and competitive analysis 2024-2025"

**Business Requirements**:
- Understand current market trends and growth trajectory
- Identify key players and their competitive positioning
- Assess emerging opportunities and potential risks
- Generate actionable investment recommendations

**Time Constraint**: Results needed within hours, not days

---

## Expected System Behavior

### Phase 1: Planning (Orchestrator)

The Orchestrator agent should:
1. Analyze the query and decompose it into 3-5 research tasks
2. Prioritize tasks based on strategic importance
3. Create a structured research plan

**Expected Tasks**:
- Market size and growth trends for AI agent frameworks
- Competitive landscape analysis (LangGraph, CrewAI, AutoGen, etc.)
- Key technology developments and innovations
- Market opportunities and investment potential
- Risk factors and challenges

---

### Phase 2: Research (Research Agent)

The Research Agent should:
1. Generate specific search queries for each task
2. Execute real web searches via Tavily API
3. Evaluate source quality and relevance
4. Extract and structure findings

**Expected Behavior**:
- Generate 2-3 queries per task
- Filter low-quality sources (quality score < 0.4)
- Avoid duplicate research
- Gather 15-20 high-quality findings

**Sample Search Queries**:
```
- "AI agent frameworks market size 2024 growth forecast"
- "LangGraph vs CrewAI vs AutoGen comparison"
- "enterprise adoption AI agents LangChain"
- "venture capital investment AI agent platforms 2024"
- "challenges limitations multi-agent frameworks"
```

---

### Phase 3: Analysis (Analyst Agent)

The Analyst Agent should:
1. Synthesize findings into strategic insights
2. Identify patterns and trends across sources
3. Generate actionable recommendations
4. Evaluate research quality

**Expected Outputs**:

**Insights** (5-7 expected):
- Market trend: "Rapid enterprise adoption of AI agents in 2024"
- Competitive analysis: "LangGraph emerging as leader in state management"
- Opportunity: "Significant gap in agent observability tools"
- Risk: "Framework fragmentation creating integration challenges"

**Recommendations** (3-5 expected):
- "Invest in LangGraph ecosystem - High impact, Medium effort"
- "Explore observability/monitoring tool opportunities - High impact, High effort"
- "Monitor open-source community momentum - Low effort, Medium impact"

---

### Phase 4: Quality Evaluation & Decision

The Orchestrator should evaluate:
- **Coverage Score**: Are all planned tasks completed?
- **Source Quality**: Average quality of sources
- **Insight Depth**: Number and confidence of insights

**Decision Logic**:
```
IF coverage >= 80% AND source_quality >= 70% AND insights >= 5:
    → Finalize report
ELSE IF iteration < max_iterations:
    → Continue research (refine plan)
ELSE:
    → Finalize with available data
```

---

### Phase 5: Iteration (If Needed)

If quality insufficient, system should:
1. Identify gaps in research
2. Generate refined search queries
3. Conduct targeted additional research
4. Re-analyze with expanded dataset

**Adaptive Behavior**:
- If competitor analysis weak → More searches on specific frameworks
- If market data sparse → Broaden time range or geographic scope
- If sources low quality → Adjust domain filtering

---

## Success Metrics

### Functional Requirements
- ✅ System completes autonomously without human intervention
- ✅ All 3 agents execute their roles correctly
- ✅ Real external API calls made (Tavily)
- ✅ State properly managed across iterations
- ✅ No duplicate research performed
- ✅ Errors handled gracefully

### Quality Requirements
- ✅ 15+ relevant findings gathered
- ✅ 5+ strategic insights generated
- ✅ 3+ actionable recommendations provided
- ✅ Average source quality > 0.6
- ✅ Coverage of all major topics

### Performance Requirements
- ✅ Completes in 2-4 minutes (with API calls)
- ✅ Max 3 iterations
- ✅ < 20 API calls total
- ✅ Estimated cost < $0.50

---

## Expected Final Report Structure

```json
{
  "query": "AI agent frameworks market landscape...",
  "summary": "Executive summary of research...",
  "insights": [
    {
      "category": "market_trend",
      "description": "Insight text...",
      "confidence": 0.85,
      "priority": 5
    },
    ...
  ],
  "recommendations": [
    {
      "title": "Recommendation title",
      "description": "What to do",
      "rationale": "Why it matters",
      "impact": "high",
      "effort": "medium"
    },
    ...
  ],
  "sources": [
    {
      "title": "Source title",
      "url": "https://...",
      "quality_score": 0.8
    },
    ...
  ],
  "quality_metrics": {
    "coverage_score": 0.85,
    "source_quality_score": 0.72,
    "insight_depth_score": 0.78
  },
  "metadata": {
    "iterations": 2,
    "total_findings": 18,
    "api_calls": 12,
    "completed_at": "2024-..."
  }
}
```

---

## Testing Variations

### Variation 1: Broad Query
**Query**: "Electric vehicle market trends"
**Expected**: System should narrow down to specific aspects (market size, key players, technology)

### Variation 2: Specific Query
**Query**: "Tesla vs Rivian competitive positioning in US luxury EV segment"
**Expected**: Focused, deep-dive research with detailed comparisons

### Variation 3: Emerging Topic
**Query**: "Quantum computing commercialization prospects"
**Expected**: System handles limited sources, acknowledges uncertainty

### Variation 4: Multi-faceted Query
**Query**: "Impact of AI regulation on startup ecosystem in EU"
**Expected**: Research across multiple dimensions (regulatory, business, geographic)

---

## Demonstration Script

1. **Setup**
   ```bash
   cd 02_implementation
   cp .env.example .env
   # Add API keys to .env
   pip install -r requirements.txt
   ```

2. **Run Research**
   ```bash
   python main.py
   ```

3. **Observe Execution**
   - Watch agent transitions in logs
   - Monitor API calls
   - Track quality metrics evolution

4. **Evaluate Results**
   - Review generated insights
   - Assess recommendation quality
   - Verify source credibility

5. **Test Edge Cases**
   - Run with no API key (fallback behavior)
   - Run with max_iterations=1 (quality compromise)
   - Run with very broad query (task decomposition)

---

## Expected Log Output (Sample)

```json
{"event": "research_started", "query": "AI agent frameworks...", "timestamp": "..."}
{"event": "plan_node_executing", "iteration": 0}
{"event": "orchestrator_plan_created", "task_count": 4}
{"event": "research_node_executing", "iteration": 1}
{"event": "tavily_search", "query": "AI agent frameworks market size 2024"}
{"event": "research_completed", "findings_count": 5}
{"event": "analyst_node_executing", "iteration": 1}
{"event": "insights_generated", "count": 3}
{"event": "quality_check", "coverage": 0.75, "source_quality": 0.68}
{"event": "routing_decision", "decision": "continue"}
{"event": "plan_node_executing", "iteration": 2}
{"event": "research_node_executing", "iteration": 2}
{"event": "analyst_node_executing", "iteration": 2}
{"event": "quality_check", "coverage": 0.85, "source_quality": 0.72}
{"event": "routing_decision", "decision": "finalize"}
{"event": "research_completed", "insights_count": 6}
```

---

## Validation Checklist

After running the demonstration:

- [ ] All agents executed successfully
- [ ] Real API calls made (check logs for `tavily_search_success`)
- [ ] No duplicate searches (check `search_queries_used` in state)
- [ ] Findings have quality scores
- [ ] Insights linked to supporting findings
- [ ] Recommendations have impact/effort assessments
- [ ] Quality metrics calculated
- [ ] Report is well-structured and actionable
- [ ] Errors (if any) were handled gracefully
- [ ] Total cost within budget ($0.50)
