from src.modules.llm_summarizer import LLMSummarizer
from logger import logger
import asyncio

async def main():
    print("Hello from 1-1-cloudwalk-chatbot!")
    llm = LLMSummarizer()
    logger.info("started ----------------------")
    answer = await llm.generate_answer("new news about open ai")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())

