"""
Main entry point for the Autonomous Research Assistant.
Orchestrates multi-agent workflow using LangGraph.
"""

import os
import asyncio
from datetime import datetime
from typing import Literal
import structlog
from dotenv import load_dotenv, find_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state.research_state import ResearchState, create_initial_state
from agents.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from agents.analyst_agent import AnalystAgent

# Load environment variables
loaded = load_dotenv(override=True)
print("Loaded:", loaded)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


class AutonomousResearchAssistant:
    """
    Multi-agent research system coordinated by LangGraph.

    Agents:
    - Orchestrator: Plans and coordinates research
    - Research Agent: Gathers information from external sources
    - Analyst Agent: Synthesizes insights and validates quality
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the research assistant.

        Args:
            model_name: LLM model to use for agents
        """
        self.model_name = model_name

        # Initialize agents
        self.orchestrator = OrchestratorAgent(model_name=model_name)
        self.research_agent = ResearchAgent(model_name=model_name)
        self.analyst = AnalystAgent(model_name=model_name)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info("research_assistant_initialized", model=model_name)

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(ResearchState)

        # Add nodes (agents)
        workflow.add_node("planner", self._plan_node)
        workflow.add_node("researcher", self._research_node)
        workflow.add_node("analyst", self._analyst_node)
        workflow.add_node("finalizer", self._finalize_node)

        # Define entry point
        workflow.set_entry_point("planner")

        # Add edges
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "analyst")

        # Conditional routing from analyst
        workflow.add_conditional_edges(
            "analyst",
            self._should_continue,
            {
                "continue": "planner",
                "finalize": "finalizer"
            }
        )

        # End
        workflow.add_edge("finalizer", END)

        # Compile with checkpointing
        checkpointer = MemorySaver()
        compiled_workflow = workflow.compile(checkpointer=checkpointer)

        logger.info("workflow_compiled")
        return compiled_workflow

    async def _plan_node(self, state: ResearchState) -> ResearchState:
        """
        Planning node - Orchestrator creates/updates research plan.

        Args:
            state: Current state

        Returns:
            Updated state
        """
        logger.info("plan_node_executing", iteration=state["iteration_count"])

        # First iteration: create initial plan
        if state["iteration_count"] == 0:
            state = await self.orchestrator.plan_research(state)
        else:
            # Subsequent iterations: refine plan based on gaps
            logger.info("refining_plan", iteration=state["iteration_count"])

        # Get next task
        next_task = self.orchestrator.get_next_task(state)
        if next_task:
            next_task["status"] = "in_progress"
            state["current_task"] = next_task
        else:
            # No more tasks, should finalize
            state["needs_more_research"] = False

        state["iteration_count"] += 1

        return state

    async def _research_node(self, state: ResearchState) -> ResearchState:
        """
        Research node - Research agent gathers information.

        Args:
            state: Current state

        Returns:
            Updated state with findings
        """
        logger.info("research_node_executing", iteration=state["iteration_count"])

        state = await self.research_agent.execute_research(state)

        # Mark current task as completed
        if state.get("current_task"):
            self.orchestrator.mark_task_completed(
                state,
                state["current_task"]["task_id"]
            )

        return state

    async def _analyst_node(self, state: ResearchState) -> ResearchState:
        """
        Analyst node - Analyst synthesizes findings and evaluates quality.

        Args:
            state: Current state

        Returns:
            Updated state with insights and quality assessment
        """
        logger.info("analyst_node_executing", iteration=state["iteration_count"])

        state = await self.analyst.analyze_findings(state)

        return state

    def _should_continue(
        self,
        state: ResearchState
    ) -> Literal["continue", "finalize"]:
        """
        Decision function: continue research or finalize?

        Args:
            state: Current state

        Returns:
            'continue' or 'finalize'
        """
        # Use orchestrator's decision logic
        decision = asyncio.run(self.orchestrator.decide_next_action(state))

        logger.info("routing_decision", decision=decision, iteration=state["iteration_count"])

        return decision

    async def _finalize_node(self, state: ResearchState) -> ResearchState:
        """
        Finalization node - Generate final report.

        Args:
            state: Current state

        Returns:
            Final state with report
        """
        logger.info("finalizing_report")

        # Generate final report
        final_report = {
            "query": state["query"],
            "summary": self._generate_summary(state),
            "insights": state.get("insights", []),
            "recommendations": state.get("recommendations", []),
            "sources": self._extract_sources(state),
            "quality_metrics": state.get("quality_metrics"),
            "metadata": {
                "iterations": state["iteration_count"],
                "total_findings": len(state.get("findings", [])),
                "api_calls": state.get("api_calls_count", 0),
                "started_at": state["started_at"],
                "completed_at": datetime.now().isoformat()
            }
        }

        state["final_report"] = final_report
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()

        logger.info(
            "research_completed",
            insights_count=len(state.get("insights", [])),
            recommendations_count=len(state.get("recommendations", [])),
            iterations=state["iteration_count"]
        )

        return state

    def _generate_summary(self, state: ResearchState) -> str:
        """
        Generate executive summary of research.

        Args:
            state: Final state

        Returns:
            Summary string
        """
        insights = state.get("insights", [])
        findings = state.get("findings", [])

        summary_parts = [
            f"Research on: {state['query']}",
            f"\nCompleted {state['iteration_count']} research iterations.",
            f"Analyzed {len(findings)} sources and generated {len(insights)} strategic insights."
        ]

        if insights:
            summary_parts.append("\n\nKey Themes:")
            for i, insight in enumerate(insights[:3], 1):
                summary_parts.append(
                    f"{i}. [{insight.get('category', 'general')}] {insight.get('description', '')}"
                )

        return "\n".join(summary_parts)

    def _extract_sources(self, state: ResearchState) -> list:
        """
        Extract unique sources from findings.

        Args:
            state: Current state

        Returns:
            List of source references
        """
        findings = state.get("findings", [])
        sources = []
        seen_urls = set()

        for finding in findings:
            url = finding.get("source_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title": finding.get("source_title", ""),
                    "url": url,
                    "quality_score": finding.get("source_quality", 0)
                })

        # Sort by quality
        sources.sort(key=lambda s: s["quality_score"], reverse=True)

        return sources

    async def research(self, query: str, requirements: dict = None) -> dict:
        """
        Execute research workflow.

        Args:
            query: Research question/topic
            requirements: Optional parameters

        Returns:
            Final research report
        """
        logger.info("research_started", query=query)

        # Create initial state
        initial_state = create_initial_state(query, requirements)

        # Execute workflow
        try:
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": "research_1"}}
            )

            report = final_state.get("final_report")

            logger.info("research_successful", query=query)

            return report

        except Exception as e:
            logger.error("research_failed", query=query, error=str(e))
            raise


def print_report(report: dict):
    """
    Pretty print research report.

    Args:
        report: Final research report
    """
    print("\n" + "=" * 80)
    print("AUTONOMOUS RESEARCH ASSISTANT - FINAL REPORT")
    print("=" * 80)

    print(f"\n{report.get('summary', '')}")

    print("\n" + "-" * 80)
    print("STRATEGIC INSIGHTS")
    print("-" * 80)

    insights = report.get("insights", [])
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. [{insight.get('category', 'general').upper()}] "
              f"(Priority: {insight.get('priority', 3)}/5, "
              f"Confidence: {insight.get('confidence', 0):.0%})")
        print(f"   {insight.get('description', '')}")

    print("\n" + "-" * 80)
    print("RECOMMENDATIONS")
    print("-" * 80)

    recommendations = report.get("recommendations", [])
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.get('title', '')}")
        print(f"   Impact: {rec.get('impact', 'medium').upper()} | "
              f"Effort: {rec.get('effort', 'medium').upper()}")
        print(f"   {rec.get('description', '')}")
        print(f"   Rationale: {rec.get('rationale', '')}")

    print("\n" + "-" * 80)
    print("SOURCES")
    print("-" * 80)

    sources = report.get("sources", [])
    for i, source in enumerate(sources[:10], 1):
        quality_stars = "⭐" * int(source.get("quality_score", 0.5) * 5)
        print(f"{i}. [{quality_stars}] {source.get('title', 'Unknown')}")
        print(f"   {source.get('url', '')}")

    print("\n" + "-" * 80)
    print("METADATA")
    print("-" * 80)

    metadata = report.get("metadata", {})
    print(f"Iterations: {metadata.get('iterations', 0)}")
    print(f"Total Findings: {metadata.get('total_findings', 0)}")
    print(f"API Calls: {metadata.get('api_calls', 0)}")
    print(f"Completed: {metadata.get('completed_at', 'Unknown')}")

    metrics = report.get("quality_metrics", {})
    if metrics:
        print(f"\nQuality Metrics:")
        print(f"  Coverage: {metrics.get('coverage_score', 0):.0%}")
        print(f"  Source Quality: {metrics.get('source_quality_score', 0):.0%}")
        print(f"  Insight Depth: {metrics.get('insight_depth_score', 0):.0%}")

    print("\n" + "=" * 80)


async def main():
    """Main execution"""
    # Initialize assistant
    assistant = AutonomousResearchAssistant(model_name="gpt-4")

    # Example research query
    query = "AI agent frameworks market landscape and competitive analysis"

    # Execute research
    report = await assistant.research(
        query=query,
        requirements={
            "max_iterations": 3,
            "focus_areas": ["market_trends", "competitors", "opportunities"]
        }
    )

    # Print report
    print_report(report)


if __name__ == "__main__":
    asyncio.run(main())
