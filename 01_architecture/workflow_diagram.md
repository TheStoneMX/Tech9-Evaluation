# System Workflow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUT                               │
│            "Research AI agent frameworks market"             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGGRAPH ORCHESTRATION                     │
│                    (State Management)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌──────────┐
                  │  START   │
                  └─────┬────┘
                        │
                        ▼
        ╔═══════════════════════════════╗
        ║   PLANNER NODE                ║
        ║   (Orchestrator Agent)        ║
        ║                               ║
        ║   • Decompose query           ║
        ║   • Create research plan      ║
        ║   • Select next task          ║
        ║   • Track progress            ║
        ╚═══════════════╤═══════════════╝
                        │
                        ▼
        ╔═══════════════════════════════╗
        ║   RESEARCHER NODE             ║
        ║   (Research Agent)            ║
        ║                               ║
        ║   • Generate search queries   ║
        ║   • Call Tavily API           ║
        ║   • Evaluate sources          ║
        ║   • Extract findings          ║
        ╚═══════════════╤═══════════════╝
                        │
                        ▼
        ╔═══════════════════════════════╗
        ║   ANALYST NODE                ║
        ║   (Analyst Agent)             ║
        ║                               ║
        ║   • Synthesize findings       ║
        ║   • Generate insights         ║
        ║   • Create recommendations    ║
        ║   • Evaluate quality          ║
        ╚═══════════════╤═══════════════╝
                        │
                        ▼
                 ┌──────────────┐
                 │  DECISION    │
                 │  POINT       │
                 └──┬────────┬──┘
                    │        │
          Quality   │        │  Quality
         Sufficient │        │  Insufficient
                    │        │
                    ▼        ▼
              ╔═════════╗   │
              ║ FINALIZE║   │ (Loop back)
              ║  NODE   ║   │
              ╚════╤════╝   │
                   │        │
                   │        └──────────────┐
                   │                       │
                   ▼                       ▼
            ┌──────────┐            ┌──────────┐
            │   END    │            │ PLANNER  │
            │ (Report) │            │ (Refine) │
            └──────────┘            └──────────┘
```

## Detailed Agent Interaction Flow

```
Iteration 1:
───────────
  ORCHESTRATOR                RESEARCH AGENT              ANALYST AGENT
       │                             │                          │
       │ 1. Plan tasks               │                          │
       ├──────────────────────────►  │                          │
       │                             │                          │
       │                             │ 2. Execute searches      │
       │                             ├─────────────────────────►│
       │                             │                          │
       │                             │                          │ 3. Analyze & evaluate
       │                             │ ◄────────────────────────┤
       │                             │                          │
       │ 4. Quality check            │                          │
       ◄─────────────────────────────┼──────────────────────────┤
       │                             │                          │
       │ Decision: Continue          │                          │
       │                             │                          │

Iteration 2 (if needed):
────────────────────────
  ORCHESTRATOR                RESEARCH AGENT              ANALYST AGENT
       │                             │                          │
       │ 5. Refine plan              │                          │
       │    (address gaps)           │                          │
       ├──────────────────────────►  │                          │
       │                             │                          │
       │                             │ 6. Targeted research     │
       │                             ├─────────────────────────►│
       │                             │                          │
       │                             │                          │ 7. Deep analysis
       │                             │ ◄────────────────────────┤
       │                             │                          │
       │ 8. Final quality check      │                          │
       ◄─────────────────────────────┼──────────────────────────┤
       │                             │                          │
       │ Decision: Finalize          │                          │
       │                             │                          │
       ▼                             ▼                          ▼
   Generate Final Report
```

## State Transitions

```
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌───────────┐
│ PLANNING │────►│RESEARCHING │────►│ ANALYZING  │────►│COMPLETED  │
└──────────┘     └────────────┘     └────────────┘     └───────────┘
      ▲                                     │
      │                                     │
      └─────────────────────────────────────┘
              (needs_more_research)
```

## Data Flow

```
INPUT: Research Query
   │
   ▼
┌────────────────────────────────────┐
│  SHARED STATE (ResearchState)     │
│  ─────────────────────────────     │
│  • query                           │
│  • research_plan: [tasks]          │
│  • findings: [...]     ────────┐   │
│  • insights: [...]             │   │
│  • recommendations: [...]      │   │
│  • quality_metrics: {...}      │   │
│  • iteration_count: N          │   │
└────────────────────────────────────┘
                 │                │
                 │                │
    ┌────────────┼────────────┐   │
    │            │            │   │
    ▼            ▼            ▼   │
┌────────┐  ┌────────┐  ┌────────┴───┐
│Orchestr│  │Research│  │  Analyst   │
│  ator  │  │ Agent  │  │   Agent    │
└────────┘  └────────┘  └────────────┘
    │            │            │
    │            │            │
    └────────────┼────────────┘
                 │
                 ▼
          Final Report
```

## External API Integration Points

```
                    RESEARCH AGENT
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Tavily  │    │  News   │    │  Other  │
    │   API   │    │   API   │    │  APIs   │
    └─────────┘    └─────────┘    └─────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                   Findings Pool
                         │
                         ▼
                   ANALYST AGENT
```

## Error Handling Flow

```
         ┌─────────────┐
         │   Agent     │
         │  Executes   │
         └──────┬──────┘
                │
           ┌────┴────┐
           │         │
        Success    Error
           │         │
           │         ▼
           │    ┌──────────┐
           │    │  Retry   │
           │    │  Logic   │
           │    └────┬─────┘
           │         │
           │    ┌────┴────┐
           │    │         │
           │  Success   Fail
           │    │         │
           │    │         ▼
           │    │    ┌─────────────┐
           │    │    │   Fallback  │
           │    │    │   Strategy  │
           │    │    └──────┬──────┘
           │    │           │
           └────┴───────────┴───►
                    │
                    ▼
               Continue/Log Error
```

## Coordination Mechanism

```
ORCHESTRATOR decides:
  │
  ├─► Task Priority
  ├─► Next Action
  ├─► Quality Threshold
  └─► Stop Condition

RESEARCH AGENT tracks:
  │
  ├─► Covered Topics
  ├─► Used Queries
  └─► Source Quality

ANALYST AGENT evaluates:
  │
  ├─► Insight Quality
  ├─► Coverage Gaps
  └─► Need for More Data
```

## Key Features Illustrated

1. **Autonomous Decision Making**: Agents decide next steps based on state
2. **Feedback Loops**: Analyst can request more research
3. **State Management**: Centralized state prevents duplicate work
4. **Quality Gates**: Multiple checkpoints before finalization
5. **Error Resilience**: Retry logic and fallback strategies
6. **External Integration**: Real API calls for data gathering
