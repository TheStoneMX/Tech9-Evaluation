"""
Orchestrator Agent - Strategic planning and coordination
"""

import uuid
from datetime import datetime
from typing import Optional
import structlog
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from state.research_state import (
    ResearchState,
    ResearchTask,
    calculate_quality_metrics,
    is_quality_sufficient
)

logger = structlog.get_logger()


class OrchestratorAgent:
    """
    Orchestrator Agent responsible for:
    - Decomposing research queries into subtasks
    - Planning research strategy
    - Coordinating between Research and Analyst agents
    - Making decisions about when to continue or finalize
    """

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        """
        Initialize the Orchestrator Agent.

        Args:
            model_name: LLM model to use
            temperature: Model temperature for planning
        """
        self.model_name = model_name

        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        logger.info("orchestrator_initialized", model=model_name)

    async def plan_research(self, state: ResearchState) -> ResearchState:
        """
        Create a research plan by decomposing the query into subtasks.

        Args:
            state: Current research state

        Returns:
            Updated state with research plan
        """
        logger.info("orchestrator_planning", query=state["query"])

        query = state["query"]
        requirements = state.get("requirements", {})

        # Create planning prompt
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strategic research planner. Given a research query,
            decompose it into 3-5 specific, actionable research subtasks.

            Consider:
            - Market trends and dynamics
            - Competitive landscape
            - Key players and stakeholders
            - Recent developments and news
            - Strategic opportunities and risks

            Return a structured plan."""),
            ("user", """Research Query: {query}

            Requirements: {requirements}

            Create a research plan with specific subtasks. For each task, provide:
            1. Task description
            2. Topic/focus area
            3. Priority (1-5, where 5 is highest)

            Format your response as a JSON array of tasks:
            [
              {{"description": "...", "topic": "...", "priority": 5}},
              ...
            ]""")
        ])

        try:
            # Get planning from LLM
            chain = planning_prompt | self.llm
            response = await chain.ainvoke({
                "query": query,
                "requirements": str(requirements)
            })

            # Parse response
            content = response.content
            tasks = self._parse_tasks(content, query)

            state["research_plan"] = tasks
            state["status"] = "researching"

            logger.info(
                "orchestrator_plan_created",
                task_count=len(tasks),
                topics=[t["topic"] for t in tasks]
            )

            return state

        except Exception as e:
            logger.error("orchestrator_planning_error", error=str(e))
            # Fallback to basic plan
            state["research_plan"] = self._create_fallback_plan(query)
            state["status"] = "researching"
            return state

    def _parse_tasks(self, content: str, query: str) -> list[ResearchTask]:
        """
        Parse LLM response into structured tasks.

        Args:
            content: LLM response
            query: Original query

        Returns:
            List of ResearchTask objects
        """
        import json
        import re

        tasks = []

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())

                for i, task_data in enumerate(tasks_data):
                    task = ResearchTask(
                        task_id=str(uuid.uuid4()),
                        description=task_data.get("description", ""),
                        topic=task_data.get("topic", ""),
                        priority=task_data.get("priority", 3),
                        status="pending"
                    )
                    tasks.append(task)

        except Exception as e:
            logger.warning("task_parsing_failed", error=str(e))
            # Fallback
            tasks = self._create_fallback_plan(query)

        return tasks

    def _create_fallback_plan(self, query: str) -> list[ResearchTask]:
        """
        Create a basic research plan when LLM planning fails.

        Args:
            query: Research query

        Returns:
            List of basic research tasks
        """
        logger.info("creating_fallback_plan", query=query)

        return [
            ResearchTask(
                task_id=str(uuid.uuid4()),
                description=f"Research market trends for {query}",
                topic="market_trends",
                priority=5,
                status="pending"
            ),
            ResearchTask(
                task_id=str(uuid.uuid4()),
                description=f"Analyze competitive landscape for {query}",
                topic="competitive_analysis",
                priority=4,
                status="pending"
            ),
            ResearchTask(
                task_id=str(uuid.uuid4()),
                description=f"Identify key players and stakeholders in {query}",
                topic="stakeholder_analysis",
                priority=3,
                status="pending"
            )
        ]

    async def decide_next_action(self, state: ResearchState) -> str:
        """
        Decide whether to continue research or finalize.

        Args:
            state: Current research state

        Returns:
            'continue' or 'finalize'
        """
        logger.info("orchestrator_deciding", iteration=state["iteration_count"])

        # Check iteration limit
        if state["iteration_count"] >= state["max_iterations"]:
            logger.info("max_iterations_reached", iterations=state["iteration_count"])
            return "finalize"

        # Calculate quality metrics
        metrics = calculate_quality_metrics(state)
        state["quality_metrics"] = metrics

        logger.info(
            "quality_check",
            coverage=metrics["coverage_score"],
            source_quality=metrics["source_quality_score"],
            insight_depth=metrics["insight_depth_score"]
        )

        # Check if quality is sufficient
        if is_quality_sufficient(metrics):
            logger.info("quality_sufficient", metrics=metrics)
            return "finalize"

        # Check if analyst requested more research
        if state.get("needs_more_research", True):
            logger.info("analyst_requested_more_research")
            return "continue"

        # Check for critical errors
        if state.get("has_critical_error", False):
            logger.warning("critical_error_detected", finalizing=True)
            return "finalize"

        # Default: one more iteration if we have findings
        if state.get("findings"):
            logger.info("continuing_to_improve_quality")
            return "continue"
        else:
            logger.info("no_findings_finalizing")
            return "finalize"

    def get_next_task(self, state: ResearchState) -> Optional[ResearchTask]:
        """
        Get the next pending task from the research plan.

        Args:
            state: Current research state

        Returns:
            Next task or None if all completed
        """
        plan = state.get("research_plan", [])

        # Sort by priority and get first pending
        pending_tasks = [t for t in plan if t.get("status") == "pending"]
        if not pending_tasks:
            return None

        # Sort by priority (highest first)
        pending_tasks.sort(key=lambda t: t.get("priority", 0), reverse=True)

        next_task = pending_tasks[0]
        logger.info("next_task_selected", task=next_task["description"])

        return next_task

    def mark_task_completed(self, state: ResearchState, task_id: str) -> ResearchState:
        """
        Mark a task as completed.

        Args:
            state: Current research state
            task_id: ID of task to mark completed

        Returns:
            Updated state
        """
        for task in state.get("research_plan", []):
            if task.get("task_id") == task_id:
                task["status"] = "completed"
                logger.info("task_completed", task_id=task_id)
                break

        return state
