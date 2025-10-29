import base64
import io
import os
import re
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from logger import logger

from src.modules.llm_summarizer import LLMSummarizer

class Message(BaseModel):
    message: str

# Initialize the FastAPI app
app = FastAPI()

app.mount("/public", StaticFiles(directory="./public"), name="public")
# # Add CORS middleware to allow all origins, methods, and headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "./public/index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    logger.info('Web app started')
    return HTMLResponse(content=html_content)

@app.post("/generate_response")
async def generate_response(message_data: Message):
    """
    Generate a response to a user message, checking for prompt injection before replying

    :param message_data: The message data containing the user's input
    :type message_data: Message
    :return: The generated response string based on prompt injection check
    :rtype: str
    """
    user_message = message_data.message.lower().strip()

    logger.info('Generate response started')
    logger.info(f'User message,{user_message}')

    answer = ''
    if not check_for_prompt_injection(user_message):
        llm_summarizer = LLMSummarizer()
        answer = await llm_summarizer.generate_answer(user_message)
    else:
        answer = 'Please ask different questions, I am unable to answer that question.'
    return answer    

def check_for_prompt_injection(user_query: str) -> bool:
    """
    Performs a basic check for common prompt injection patterns 
    in the user query.

    Args:
        user_query: The input string from the user.

    Returns:
        True if potential injection is detected, False otherwise.
    """
    logger.info('Checking for prompt injection')
    # 1. Normalize the query for case-insensitive matching
    normalized_query = user_query.lower().strip()

    # 2. Define known trigger phrases and commands
    # These often instruct the model to ignore prior context or reveal system instructions
    injection_triggers = [
        "ignore previous instructions",
        "disregard all previous",
        "new instructions:",
        "act as a",
        "as an ai language model",
        "system prompt",
        "show me your prompt",
        "print out the following",
        "developer mode",
        "jailbreak",
        "i am a developer",
        "forget everything"
    ]

    # 3. Check for high-density symbols used to break context or formatting
    # A high concentration of symbols suggests manipulation
    symbol_density_threshold = 0.25  # e.g., 25% of the query is symbols
    
    # Count non-alphanumeric characters (excluding spaces)
    symbol_count = sum(
        1 for char in normalized_query 
        if not char.isalnum() and not char.isspace()
    )
    
    # Calculate density relative to the length of the query
    if len(normalized_query) > 15 and (symbol_count / len(normalized_query)) > symbol_density_threshold:
        return True

    # 4. Check for known trigger phrases
    for trigger in injection_triggers:
        if trigger in normalized_query:
            logger.warning('Potential prompt injection attempt detected and blocked')
            
            return True

    # If no obvious signs of injection are found
    logger.info('There is not prompt injection')
    return False

# if __name__ == "__main__":
#     # Run the server with Uvicorn.
#     uvicorn.run(app, host="0.0.0.0", port=8000)