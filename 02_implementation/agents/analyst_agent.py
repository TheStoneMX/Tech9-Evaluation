"""
Analyst Agent - Synthesis, validation, and insight generation
"""

import uuid
from datetime import datetime
from typing import List, Dict
import structlog
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from state.research_state import (
    ResearchState,
    Insight,
    Recommendation,
    calculate_quality_metrics,
    is_quality_sufficient
)

logger = structlog.get_logger()


class AnalystAgent:
    """
    Analyst Agent responsible for:
    - Synthesizing research findings into insights
    - Validating research quality
    - Generating strategic recommendations
    - Deciding if more research is needed
    """

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.4):
        """
        Initialize the Analyst Agent.

        Args:
            model_name: LLM model to use
            temperature: Model temperature for creative analysis
        """
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        logger.info("analyst_agent_initialized", model=model_name)

    async def analyze_findings(self, state: ResearchState) -> ResearchState:
        """
        Analyze research findings and generate insights.

        Args:
            state: Current research state

        Returns:
            Updated state with insights and recommendations
        """
        findings = state.get("findings", [])

        if not findings:
            logger.warning("no_findings_to_analyze")
            state["needs_more_research"] = True
            return state

        logger.info(
            "analyst_analyzing",
            findings_count=len(findings),
            iteration=state["iteration_count"]
        )

        try:
            # Generate insights from findings
            insights = await self._generate_insights(findings, state)
            # Replace insights instead of extending to avoid duplication across iterations
            state["insights"] = insights

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                insights,
                findings,
                state
            )
            # Replace recommendations instead of extending to avoid duplication across iterations
            state["recommendations"] = recommendations

            # Evaluate if more research is needed
            needs_more = await self._evaluate_completeness(state)
            state["needs_more_research"] = needs_more

            logger.info(
                "analyst_completed",
                insights_count=len(insights),
                recommendations_count=len(recommendations),
                needs_more_research=needs_more
            )

            return state

        except Exception as e:
            logger.error(
                "analyst_error",
                error=str(e),
                error_type=type(e).__name__
            )

            state["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": "analyst",
                "error_type": type(e).__name__,
                "message": str(e),
                "recoverable": True
            })

            # Conservative: request more research on error
            state["needs_more_research"] = True
            return state

    async def _generate_insights(
        self,
        findings: List[Dict],
        state: ResearchState
    ) -> List[Insight]:
        """
        Generate strategic insights from research findings.

        Args:
            findings: Research findings
            state: Current state

        Returns:
            List of Insight objects
        """
        logger.info("generating_insights", findings_count=len(findings))

        # Prepare findings summary for LLM
        findings_text = self._prepare_findings_summary(findings)

        insight_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strategic business analyst. Analyze research findings
            and identify key insights across these categories:
            - Market trends
            - Competitive dynamics
            - Strategic opportunities
            - Potential risks

            For each insight:
            1. Clearly state the insight
            2. Categorize it
            3. Assess confidence level (0-1)
            4. Assign strategic priority (1-5)

            Return insights in JSON format."""),
            ("user", """Research Query: {query}

            Findings Summary:
            {findings}

            Generate 3-7 strategic insights. Format:
            [
              {{
                "category": "market_trend|competitor_analysis|opportunity|risk",
                "description": "Clear insight statement",
                "confidence": 0.0-1.0,
                "priority": 1-5
              }},
              ...
            ]""")
        ])

        try:
            chain = insight_prompt | self.llm
            response = await chain.ainvoke({
                "query": state["query"],
                "findings": findings_text
            })

            # Parse insights
            insights = self._parse_insights(response.content, findings)

            logger.info("insights_generated", count=len(insights))
            return insights

        except Exception as e:
            logger.warning("insight_generation_failed", error=str(e))
            return []

    async def _generate_recommendations(
        self,
        insights: List[Insight],
        findings: List[Dict],
        state: ResearchState
    ) -> List[Recommendation]:
        """
        Generate actionable recommendations from insights.

        Args:
            insights: Strategic insights
            findings: Research findings
            state: Current state

        Returns:
            List of Recommendation objects
        """
        if not insights:
            logger.info("no_insights_for_recommendations")
            return []

        logger.info("generating_recommendations", insights_count=len(insights))

        insights_text = "\n".join([
            f"- [{i.get('category', 'general')}] {i.get('description', '')} "
            f"(Priority: {i.get('priority', 3)})"
            for i in insights
        ])

        rec_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strategic advisor. Based on research insights,
            generate 3-5 actionable recommendations for decision makers.

            For each recommendation:
            - Clear, action-oriented title
            - Detailed description
            - Rationale tied to insights
            - Impact assessment (high/medium/low)
            - Effort assessment (high/medium/low)

            Return in JSON format."""),
            ("user", """Research Query: {query}

            Strategic Insights:
            {insights}

            Generate 3-5 actionable recommendations. Format:
            [
              {{
                "title": "Action-oriented title",
                "description": "What to do",
                "rationale": "Why this matters",
                "impact": "high|medium|low",
                "effort": "high|medium|low"
              }},
              ...
            ]""")
        ])

        try:
            chain = rec_prompt | self.llm
            response = await chain.ainvoke({
                "query": state["query"],
                "insights": insights_text
            })

            # Parse recommendations
            recommendations = self._parse_recommendations(response.content, insights)

            logger.info("recommendations_generated", count=len(recommendations))
            return recommendations

        except Exception as e:
            logger.warning("recommendation_generation_failed", error=str(e))
            return []

    async def _evaluate_completeness(self, state: ResearchState) -> bool:
        """
        Evaluate if more research is needed.

        Args:
            state: Current state

        Returns:
            True if more research needed
        """
        # Calculate quality metrics
        metrics = calculate_quality_metrics(state)

        logger.info(
            "evaluating_completeness",
            coverage=metrics["coverage_score"],
            source_quality=metrics["source_quality_score"],
            insight_depth=metrics["insight_depth_score"],
            iteration=state["iteration_count"]
        )

        # Check if quality is sufficient
        if is_quality_sufficient(metrics):
            logger.info("quality_sufficient_no_more_research")
            return False

        # Check if we have at least some good insights
        insights = state.get("insights", [])
        high_confidence_insights = [
            i for i in insights
            if i.get("confidence", 0) >= 0.7
        ]

        if len(high_confidence_insights) >= 5:
            logger.info("sufficient_high_confidence_insights")
            return False

        # Check iteration count
        if state["iteration_count"] >= state["max_iterations"] - 1:
            logger.info("near_max_iterations_finalizing")
            return False

        # Need more research
        logger.info("requesting_more_research")
        return True

    def _prepare_findings_summary(self, findings: List[Dict]) -> str:
        """
        Prepare a concise summary of findings for LLM processing.

        Args:
            findings: Research findings

        Returns:
            Formatted summary string
        """
        # Group by topic/source quality
        summary_parts = []

        for i, finding in enumerate(findings[:20], 1):  # Limit to top 20
            quality_indicator = "⭐" * int(finding.get("source_quality", 0.5) * 5)
            summary_parts.append(
                f"{i}. [{quality_indicator}] {finding.get('source_title', 'Unknown')}\n"
                f"   {finding.get('content', '')[:200]}..."
            )

        return "\n\n".join(summary_parts)

    def _parse_insights(self, content: str, findings: List[Dict]) -> List[Insight]:
        """
        Parse LLM response into Insight objects.

        Args:
            content: LLM response
            findings: Source findings

        Returns:
            List of Insight objects
        """
        import json
        import re

        insights = []

        try:
            # Extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                insights_data = json.loads(json_match.group())

                for data in insights_data:
                    # Get relevant finding IDs (simplified)
                    supporting_findings = [
                        f.get("finding_id", "")
                        for f in findings[:3]  # Top 3 findings as support
                    ]

                    insight = Insight(
                        insight_id=str(uuid.uuid4()),
                        category=data.get("category", "general"),
                        description=data.get("description", ""),
                        supporting_findings=supporting_findings,
                        confidence=float(data.get("confidence", 0.7)),
                        priority=int(data.get("priority", 3))
                    )
                    insights.append(insight)

        except Exception as e:
            logger.warning("insight_parsing_failed", error=str(e))

        return insights

    def _parse_recommendations(
        self,
        content: str,
        insights: List[Insight]
    ) -> List[Recommendation]:
        """
        Parse LLM response into Recommendation objects.

        Args:
            content: LLM response
            insights: Source insights

        Returns:
            List of Recommendation objects
        """
        import json
        import re

        recommendations = []

        try:
            # Extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                recs_data = json.loads(json_match.group())

                for data in recs_data:
                    # Link to supporting insights
                    supporting_insights = [
                        i.get("insight_id", "")
                        for i in insights[:2]  # Top 2 insights
                    ]

                    rec = Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title=data.get("title", ""),
                        description=data.get("description", ""),
                        rationale=data.get("rationale", ""),
                        supporting_insights=supporting_insights,
                        impact=data.get("impact", "medium"),
                        effort=data.get("effort", "medium")
                    )
                    recommendations.append(rec)

        except Exception as e:
            logger.warning("recommendation_parsing_failed", error=str(e))

        return recommendations
