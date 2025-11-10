"""
Research Agent - Information gathering and source evaluation
"""

import uuid
from datetime import datetime
from typing import List
import structlog
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from state.research_state import ResearchState, Finding, ResearchTask
from tools.search_tools import SearchTools

logger = structlog.get_logger()


class ResearchAgent:
    """
    Research Agent responsible for:
    - Executing web searches based on tasks
    - Evaluating source credibility and relevance
    - Extracting key information from sources
    - Avoiding duplicate research
    """

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize the Research Agent.

        Args:
            model_name: LLM model to use
            temperature: Model temperature for analysis
        """
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.search_tools = SearchTools()

        logger.info("research_agent_initialized", model=model_name)

    async def execute_research(self, state: ResearchState) -> ResearchState:
        """
        Execute research for the current task.

        Args:
            state: Current research state

        Returns:
            Updated state with research findings
        """
        current_task = state.get("current_task")
        if not current_task:
            logger.warning("no_current_task")
            return state

        logger.info(
            "research_agent_executing",
            task=current_task["description"],
            task_id=current_task["task_id"]
        )

        try:
            # Generate search queries for this task
            queries = await self._generate_search_queries(current_task, state)

            # Execute searches
            all_results = []
            for query in queries:
                # Skip if we've already searched this
                if query in state.get("search_queries_used", []):
                    logger.info("skipping_duplicate_query", query=query)
                    continue

                # Perform search
                results = await self.search_tools.search_web(
                    query=query,
                    max_results=5,
                    search_depth="advanced"
                )

                all_results.extend(results.get("results", []))
                state["search_queries_used"].append(query)
                state["api_calls_count"] = state.get("api_calls_count", 0) + 1

            # Deduplicate results
            unique_results = self.search_tools.deduplicate_results(all_results)

            # Process and evaluate results
            findings = await self._process_results(
                unique_results,
                current_task,
                state
            )

            # Add findings to state
            state["findings"].extend(findings)
            state["covered_topics"].append(current_task["topic"])

            logger.info(
                "research_completed",
                task_id=current_task["task_id"],
                findings_count=len(findings),
                total_findings=len(state["findings"])
            )

            return state

        except Exception as e:
            logger.error(
                "research_error",
                task_id=current_task.get("task_id"),
                error=str(e),
                error_type=type(e).__name__
            )

            # Log error but continue
            state["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": "research",
                "error_type": type(e).__name__,
                "message": str(e),
                "recoverable": True
            })

            return state

    async def _generate_search_queries(
        self,
        task: ResearchTask,
        state: ResearchState
    ) -> List[str]:
        """
        Generate optimal search queries for a research task.

        Args:
            task: Research task
            state: Current state

        Returns:
            List of search queries
        """
        logger.info("generating_queries", task=task["description"])

        query_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating search queries.
            Given a research task, generate 2-3 specific, effective search queries
            that will find the most relevant and high-quality information.

            Make queries specific and targeted. Use advanced search techniques."""),
            ("user", """Research Task: {task_description}
            Topic: {topic}
            Original Query: {original_query}

            Generate 2-3 search queries. Return only the queries, one per line.""")
        ])

        try:
            chain = query_prompt | self.llm
            response = await chain.ainvoke({
                "task_description": task["description"],
                "topic": task["topic"],
                "original_query": state["query"]
            })

            # Parse queries from response
            queries = [
                q.strip()
                for q in response.content.split("\n")
                if q.strip() and not q.strip().startswith("#")
            ][:3]  # Max 3 queries

            logger.info("queries_generated", count=len(queries), queries=queries)

            return queries

        except Exception as e:
            logger.warning("query_generation_failed", error=str(e))
            # Fallback to simple query
            return [task["description"]]

    async def _process_results(
        self,
        results: list,
        task: ResearchTask,
        state: ResearchState
    ) -> List[Finding]:
        """
        Process search results into structured findings.

        Args:
            results: Raw search results
            task: Current research task
            state: Current state

        Returns:
            List of Finding objects
        """
        findings = []

        for result in results:
            # Evaluate source quality
            source_quality = self.search_tools.evaluate_source_quality(
                url=result.get("url", ""),
                title=result.get("title", ""),
                content=result.get("content", "")
            )

            # Calculate relevance
            relevance = self.search_tools.calculate_relevance(
                query=task["description"],
                content=result.get("content", ""),
                title=result.get("title", "")
            )

            # Only include if meets minimum quality threshold
            if source_quality >= 0.4 and relevance >= 0.3:
                finding = Finding(
                    finding_id=str(uuid.uuid4()),
                    task_id=task["task_id"],
                    content=result.get("content", ""),
                    source_url=result.get("url", ""),
                    source_title=result.get("title", ""),
                    source_quality=source_quality,
                    relevance_score=relevance,
                    timestamp=datetime.now().isoformat()
                )
                findings.append(finding)

        logger.info(
            "results_processed",
            total_results=len(results),
            qualified_findings=len(findings)
        )

        return findings

    def is_topic_covered(self, topic: str, state: ResearchState) -> bool:
        """
        Check if a topic has already been researched.

        Args:
            topic: Topic to check
            state: Current state

        Returns:
            True if topic already covered
        """
        covered = topic.lower() in [
            t.lower() for t in state.get("covered_topics", [])
        ]

        if covered:
            logger.info("topic_already_covered", topic=topic)

        return covered

    def get_research_confidence(self, state: ResearchState) -> float:
        """
        Calculate confidence in current research completeness.

        Args:
            state: Current state

        Returns:
            Confidence score 0-1
        """
        findings = state.get("findings", [])

        if not findings:
            return 0.0

        # Factors for confidence:
        # 1. Number of findings
        count_score = min(1.0, len(findings) / 15.0)  # 15+ findings = max score

        # 2. Average source quality
        avg_quality = sum(f.get("source_quality", 0) for f in findings) / len(findings)

        # 3. Topic coverage
        plan = state.get("research_plan", [])
        covered_topics = state.get("covered_topics", [])
        coverage = len(covered_topics) / max(len(plan), 1) if plan else 0

        # Weighted combination
        confidence = (
            count_score * 0.3 +
            avg_quality * 0.4 +
            coverage * 0.3
        )

        logger.info(
            "research_confidence",
            confidence=confidence,
            findings_count=len(findings),
            avg_quality=avg_quality,
            topic_coverage=coverage
        )

        return confidence
