"""
DuckDuckGo Retriever module for CloudWalk RAG Chatbot.

This module uses the modern DDGS (DuckDuckGo Search) interface to perform
text-only web searches, fetch corresponding web pages, and extract readable
content for use in retrieval-augmented generation (RAG).

All data structures are defined in the schema directory.
"""

from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from typing import List
from src.schemas.search_result import SearchResult


class DuckDuckGoRetriever:
    """
    A text-only search retriever using DuckDuckGo's DDGS interface.

    Steps:
      1. Search DuckDuckGo for text results (no images or videos)
      2. Fetch corresponding page content using requests + BeautifulSoup
      3. Return list of SearchResult objects (title, snippet, url, domain, content)
    """

    def __init__(self, user_agent: str = "CloudWalk-RAGBot/1.0", pause: float = 0.3):
        self.user_agent = user_agent
        self.pause = pause  # seconds between requests to avoid hammering sites

    async def _fetch_page_text(self, url: str, timeout: int = 8) -> str:
        """
        Fetch HTML content of a web page and extract readable text using BeautifulSoup.
        Returns a plain text string (cleaned paragraphs).
        """
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
        except Exception:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Prefer article tag if present; otherwise fallback to main <p> tags
        article = soup.find("article")
        if article:
            paragraphs = [p.get_text(separator=" ", strip=True) for p in article.find_all("p")]
        else:
            paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]

        # Combine text and clean it up
        text = " ".join(paragraphs)
        return " ".join(text.split())

    async def search(self, query: str, max_results: int = 2) -> List[SearchResult]:
        """
        Perform a text-based DuckDuckGo search and fetch content for each result.

        Args:
            query: User query string.
            max_results: Maximum number of search results to return.

        Returns:
            List of SearchResult objects with title, snippet, url, domain, and extracted content.
        """
        results: List[SearchResult] = []

        if 'cloudwalk' in query.lower():
            query = "site:cloudwalk.io " + query
       
        with DDGS() as ddgs:
            try:
                ddg_results = list(ddgs.text(query, max_results=max_results))
            except Exception:
                return results  # return empty on failure

        for r in ddg_results:
            title = r.get("title") or ""
            snippet = r.get("body") or ""
            url = r.get("href") or r.get("url") or ""
            domain = urlparse(url).netloc if url else ""

            # Fetch readable page content
            content = await self._fetch_page_text(url)
            time.sleep(self.pause)

            result = SearchResult(
                title=title,
                snippet=snippet,
                url=url,
                domain=domain,
                content=content,
            )
            
            results.append(result)

        return results
