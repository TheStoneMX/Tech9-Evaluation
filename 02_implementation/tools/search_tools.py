"""
External API tools for research.
Includes web search, news search, and source validation.
"""

import os
from typing import Optional
from datetime import datetime
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from tavily import TavilyClient

logger = structlog.get_logger()


class SearchTools:
    """
    Wrapper for external search APIs with error handling and retries.
    """

    def __init__(self):
        """Initialize search clients"""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            logger.warning("TAVILY_API_KEY not found, search functionality limited")
            self.tavily_client = None
        else:
            self.tavily_client = TavilyClient(api_key=self.tavily_api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def search_web(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced"
    ) -> dict:
        """
        Perform web search using Tavily API.

        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: 'basic' or 'advanced'

        Returns:
            dict with results and metadata
        """
        try:
            if not self.tavily_client:
                return self._fallback_search(query, max_results)

            logger.info(
                "tavily_search",
                query=query,
                max_results=max_results,
                depth=search_depth
            )

            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True,
                include_raw_content=False
            )

            results = {
                "query": query,
                "answer": response.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0.5),
                        "published_date": r.get("published_date")
                    }
                    for r in response.get("results", [])
                ],
                "timestamp": datetime.now().isoformat(),
                "api_used": "tavily"
            }

            logger.info(
                "tavily_search_success",
                query=query,
                results_count=len(results["results"])
            )

            return results

        except Exception as e:
            logger.error(
                "tavily_search_error",
                query=query,
                error=str(e),
                error_type=type(e).__name__
            )
            # Fall back to basic search
            return self._fallback_search(query, max_results)

    def _fallback_search(self, query: str, max_results: int) -> dict:
        """
        Fallback search when Tavily is unavailable.
        Uses a simple web scraping approach.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            dict with mock results (in production, use alternative API)
        """
        logger.warning(
            "using_fallback_search",
            query=query,
            reason="tavily_unavailable"
        )

        # In production, use alternative like SerpAPI, Google Custom Search, etc.
        # For demo purposes, return structured mock data
        return {
            "query": query,
            "answer": f"Fallback search for: {query}",
            "results": [
                {
                    "title": f"Result {i+1} for {query}",
                    "url": f"https://example.com/result{i+1}",
                    "content": f"This is fallback content for {query}. "
                               f"In production, use alternative search API.",
                    "score": 0.5,
                    "published_date": None
                }
                for i in range(min(max_results, 3))
            ],
            "timestamp": datetime.now().isoformat(),
            "api_used": "fallback"
        }

    def evaluate_source_quality(self, url: str, title: str, content: str) -> float:
        """
        Evaluate the quality/credibility of a source.

        Args:
            url: Source URL
            title: Article title
            content: Article content

        Returns:
            Quality score 0-1
        """
        score = 0.5  # Base score

        # Domain authority (simple heuristic)
        trusted_domains = [
            ".gov", ".edu", "reuters.com", "bloomberg.com",
            "wsj.com", "forbes.com", "techcrunch.com",
            "harvard.edu", "stanford.edu", "mit.edu"
        ]
        for domain in trusted_domains:
            if domain in url.lower():
                score += 0.2
                break

        # Content quality indicators
        if content:
            # Longer content generally better (but cap it)
            content_quality = min(0.2, len(content) / 2000)
            score += content_quality

        # Title quality
        if title and len(title) > 20:
            score += 0.1

        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, score))

    def calculate_relevance(self, query: str, content: str, title: str) -> float:
        """
        Calculate relevance of content to query.

        Args:
            query: Original search query
            content: Article content
            title: Article title

        Returns:
            Relevance score 0-1
        """
        query_terms = set(query.lower().split())
        content_lower = (content + " " + title).lower()

        # Count matching terms
        matches = sum(1 for term in query_terms if term in content_lower)

        # Basic relevance score
        relevance = matches / max(len(query_terms), 1)

        return min(1.0, relevance)

    def deduplicate_results(self, results: list[dict]) -> list[dict]:
        """
        Remove duplicate results based on URL similarity.

        Args:
            results: List of search results

        Returns:
            Deduplicated results
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "")
            # Normalize URL
            normalized = url.lower().rstrip("/")

            if normalized not in seen_urls:
                seen_urls.add(normalized)
                unique_results.append(result)

        logger.info(
            "deduplication",
            original_count=len(results),
            unique_count=len(unique_results)
        )

        return unique_results


class NewsTools:
    """
    Tools for fetching recent news and updates.
    """

    def __init__(self):
        """Initialize news API clients"""
        # Could integrate with NewsAPI, Google News, etc.
        pass

    async def get_recent_news(
        self,
        topic: str,
        max_results: int = 5,
        days_back: int = 30
    ) -> list[dict]:
        """
        Get recent news articles about a topic.

        Args:
            topic: News topic
            max_results: Maximum articles to return
            days_back: How many days to look back

        Returns:
            List of news articles
        """
        # In production, integrate with NewsAPI or similar
        logger.info(
            "fetching_news",
            topic=topic,
            max_results=max_results,
            days_back=days_back
        )

        # For demo, return mock structure
        return [
            {
                "title": f"Recent development in {topic}",
                "url": f"https://news.example.com/{topic.replace(' ', '-')}",
                "content": f"Latest news about {topic}...",
                "published_at": datetime.now().isoformat(),
                "source": "Mock News"
            }
        ]
