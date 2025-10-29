# src/modules/llm_langchain.py
import asyncio
import os
import textwrap
from typing import List, Optional

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
# from langchain.prompts import ChatPromptTemplate

from logger import logger
from src.modules.search import DuckDuckGoRetriever
from src.schemas.search_result import SearchResult

from dotenv import load_dotenv
load_dotenv()

class LLMSummarizer:
    """
    Wrapper around an LLM backend using LangChain's ChatOpenAI and 
    a local transformers fallback for RAG-style generation.
    """

    def __init__(self, model: Optional[str] = None):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        # Use LangChain's standard environment variable loading (OPENAI_API_KEY)
        self.model = model or os.environ.get("OPENAI_MODEL")

        if self.openai_api_key:
            logger.info("LLMClient: using LangChain ChatOpenAI backend")
            # Initialize the ChatOpenAI client
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=0.0, # Set default temperature to 0.0 for factual RAG
                max_tokens=None, # Will be set per call, but leaving default None here
            )
        else:
            logger.warning("LLMClient: no OpenAI key and no transformers available; calls will fail.")
            raise ValueError("LLMClient: no OpenAI key and no transformers available; calls will fail.") 
        self.retriever = DuckDuckGoRetriever()

    async def _call_llm(self, messages: List, max_tokens: int = 512, temperature: float = 0.0) -> str:
        """
        Helper to call the initialized LangChain ChatOpenAI model.
        """
        if not self.llm:
            raise RuntimeError("LangChain LLM is not configured/initialized (Missing OPENAI_API_KEY?)")
        
        # Override the temperature for the specific call
        llm_with_params = self.llm.bind(max_tokens=max_tokens, temperature=temperature)
        
        # Invoke the model with the list of messages
        response = llm_with_params.invoke(messages)
        return response.content

    async def summarize_sources(self, sources: List[SearchResult], question: str) -> str:
        """
        Generate a concise answer to a question using only the provided search results and include source links

        :param self: The LLMSummarizer instance
        :param sources: List of search results to use for answering the question
        :type sources: List[SearchResult]
        :param question: The user's question to be answered
        :type question: str
        :return: Concise answer generated from the sources with referenced links
        :rtype: str
        """

        logger.info('initialized summarizations of web results')
        # 1. Prepare Context String
        parts = []
        for i, s in enumerate(sources, start=1):
            # Concatenate content or snippet, limiting size
            excerpt = (s.content or s.snippet or "")[:2000]
            parts.append(f"[{i}] {s.title}\nURL: {s.url}\nExcerpt: {excerpt}\n")
        context = "\n\n".join(parts)

        # 2. Define Prompts/Messages (Using LangChain ChatPromptTemplate for structure)
        system_template = (
            "You are a helpful assistant that answers user questions using ONLY the information from the "
            "provided sources. Your answers should be only 2 or 3 lines, not more than that and then appned URL where you got your answers"
            " Always include a short list of source links at the end in the form [n] URL."
        )

        user_prompt_template = textwrap.dedent("""
        Question:
        {question}

        Sources:
        {context}

        Instructions:
        - Provide a concise, direct answer in 2 or 3 lines no more than that.
        - If the answer is unsupported by the sources, say you couldn't find reliable info and include the sources.
        - At the end, include a 'Sources' list that references the numbered items, for example:
          Sources:
          [1] https://example.com/page1
          [2] https://example.org/post
        - Keep the answer focused and under ~100 words. and then make sure to add sources
        """)

        # 3. Create the list of message objects
        messages = [
            SystemMessage(content=system_template),
            HumanMessage(
                content=user_prompt_template.format(question=question, context=context)
            )
        ]

        answer = await self._call_llm(messages, max_tokens=200, temperature=0.0)
        
        return answer

    async def generate_answer(self, question: str) -> str:
        """
        Asynchronously generate a concise answer to a question using retrieved web sources

        :param self: The LLMSummarizer instance
        :param question: The user's question to be answered
        :type question: str
        :return: Concise answer generated from relevant web sources
        :rtype: str
        """
        logger.info("Generate answer method called")
        sources = await self.retriever.search(question)
        return await self.summarize_sources(sources, question)