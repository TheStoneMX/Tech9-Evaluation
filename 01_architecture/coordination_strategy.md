# Coordination Strategy

## Overview
This document describes how agents communicate, coordinate, and resolve conflicts in the Autonomous Research Assistant system.

## State Management Architecture

### LangGraph StateGraph
We use LangGraph's StateGraph for coordination because it provides:
- **Structured state management**: Type-safe state with validation
- **Automatic routing**: Conditional edges based on agent decisions
- **Checkpointing**: Built-in state persistence and recovery
- **Observability**: Native support for tracing and debugging

### State Schema
```python
class ResearchState(TypedDict):
    # Input
    query: str
    requirements: dict

    # Planning
    research_plan: list[dict]
    current_task: Optional[dict]

    # Research outputs
    findings: list[dict]
    sources: list[dict]

    # Analysis outputs
    insights: list[dict]
    recommendations: list[dict]

    # Quality metrics
    coverage_score: float
    source_quality_score: float
    insight_depth_score: float

    # Coordination
    iteration_count: int
    needs_more_research: bool
    error_log: list[str]

    # Final output
    final_report: Optional[dict]
```

---

## Communication Patterns

### 1. Sequential Coordination (Primary Pattern)
**Flow**: Orchestrator → Research → Analyst → Orchestrator (loop)

**Implementation**:
```python
graph.add_edge("orchestrator", "research")
graph.add_edge("research", "analyst")
graph.add_conditional_edges(
    "analyst",
    should_continue_research,  # Decision function
    {
        "continue": "orchestrator",
        "finalize": "end"
    }
)
```

**Benefits**:
- Clear execution order
- Easy to debug and trace
- Predictable state transitions

---

### 2. Parallel Execution (When Applicable)
**Scenario**: Research multiple independent topics simultaneously

**Implementation**:
```python
# Research Agent spawns parallel search tasks
async def research_parallel(state):
    tasks = state["research_plan"]
    results = await asyncio.gather(*[
        search_topic(task) for task in tasks
    ])
    return {"findings": results}
```

**Benefits**:
- Faster time-to-insight
- Better resource utilization

---

### 3. Feedback Loops
**Purpose**: Iterative improvement of research quality

**Mechanism**:
1. Analyst evaluates research findings
2. If quality insufficient, sets `needs_more_research = True`
3. Orchestrator creates refined research plan
4. Research Agent executes with improved queries
5. Repeat until quality threshold met (max 3 iterations)

**Quality Threshold**:
```python
def quality_sufficient(state) -> bool:
    return (
        state["coverage_score"] >= 0.8 and
        state["source_quality_score"] >= 0.7 and
        state["insight_depth_score"] >= 0.75
    )
```

---

## Conflict Resolution

### Scenario 1: Disagreement on Data Sufficiency
**Conflict**: Research Agent believes data is sufficient, Analyst wants more

**Resolution Strategy**:
```python
def resolve_sufficiency_conflict(state):
    # Orchestrator uses weighted decision
    research_confidence = state.get("research_confidence", 0)
    analyst_request_priority = state.get("analyst_priority", 0)

    if analyst_request_priority > 0.8:
        # Analyst has strong reason, continue research
        return "continue"
    elif research_confidence > 0.9 and iteration_count >= 2:
        # Diminishing returns, finalize
        return "finalize"
    else:
        # One more focused iteration
        return "continue"
```

**Outcome**: Data-driven decision with clear justification

---

### Scenario 2: Source Quality Disputes
**Conflict**: Research Agent considers source acceptable, Analyst flags as low quality

**Resolution Strategy**:
```python
def validate_source_quality(source):
    factors = {
        "domain_authority": check_domain_authority(source),
        "recency": check_publication_date(source),
        "cross_verification": check_other_sources(source),
        "bias_score": analyze_bias(source)
    }

    # Analyst has veto power on quality
    if factors["bias_score"] > 0.7:
        return "reject"

    # Weighted scoring
    quality_score = (
        factors["domain_authority"] * 0.4 +
        factors["recency"] * 0.2 +
        factors["cross_verification"] * 0.3 +
        (1 - factors["bias_score"]) * 0.1
    )

    return "accept" if quality_score >= 0.6 else "flag"
```

**Outcome**: Quantitative quality assessment with analyst override

---

## Avoiding Duplicate Work

### 1. Topic Tracking
```python
class TopicTracker:
    def __init__(self):
        self.covered_topics = set()
        self.search_queries_used = []

    def is_duplicate(self, topic: str) -> bool:
        # Semantic similarity check
        for covered in self.covered_topics:
            if semantic_similarity(topic, covered) > 0.85:
                return True
        return False

    def mark_covered(self, topic: str):
        self.covered_topics.add(topic)
```

### 2. Source Deduplication
```python
def deduplicate_sources(findings: list) -> list:
    seen_urls = set()
    unique_findings = []

    for finding in findings:
        url = normalize_url(finding["url"])
        if url not in seen_urls:
            seen_urls.add(url)
            unique_findings.append(finding)

    return unique_findings
```

### 3. State-Based Coordination
- Shared state tracks completed tasks
- Before starting new research, agent checks state for coverage
- Orchestrator ensures no overlapping assignments

---

## Error Handling & Recovery

### 1. API Failures
```python
@retry(max_attempts=3, backoff=exponential)
async def call_search_api(query):
    try:
        result = await tavily_search(query)
        return result
    except RateLimitError:
        # Fallback to alternative search
        return await fallback_search(query)
    except APIError as e:
        log_error(e)
        return {"error": str(e), "query": query}
```

### 2. Agent Failures
```python
def handle_agent_error(state, error):
    state["error_log"].append({
        "agent": error.agent_name,
        "error": str(error),
        "timestamp": datetime.now(),
        "state_snapshot": state.copy()
    })

    # Graceful degradation
    if error.agent_name == "research":
        # Continue with available data
        return route_to_analyst(state)
    elif error.agent_name == "analyst":
        # Generate basic report from raw findings
        return route_to_fallback_report(state)
```

### 3. Checkpointing
```python
# LangGraph automatic checkpointing
graph = StateGraph(ResearchState)
graph.compile(checkpointer=MemorySaver())

# Can resume from any point
state = graph.get_state(checkpoint_id)
graph.invoke(state)
```

---

## Performance Optimization

### 1. Early Termination
Stop research when quality threshold exceeded (no need for perfection)

### 2. Incremental Processing
Process and analyze findings as they arrive, don't wait for all research

### 3. Smart Caching
Cache search results and expensive LLM calls

### 4. Cost Monitoring
```python
class CostTracker:
    def __init__(self, budget: float):
        self.budget = budget
        self.spent = 0.0

    def can_continue(self) -> bool:
        return self.spent < self.budget * 0.9  # 90% threshold

    def track_call(self, tokens: int, model: str):
        cost = calculate_cost(tokens, model)
        self.spent += cost
```

---

## Observability

### Logging Strategy
```python
# Structured logging at each state transition
logger.info("state_transition", extra={
    "from_agent": "research",
    "to_agent": "analyst",
    "state_summary": {
        "findings_count": len(state["findings"]),
        "quality_score": state["source_quality_score"]
    },
    "decision_reason": "sufficient_coverage"
})
```

### Metrics Tracked
- Execution time per agent
- Number of API calls and costs
- Quality scores over iterations
- Error rates and types
- Cache hit rates

### Debugging Support
- State snapshots at each transition
- Full execution trace with LangSmith
- Replay capability from checkpoints
