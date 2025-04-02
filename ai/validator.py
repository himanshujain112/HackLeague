#import logging
import time
import uuid  # For unique request tracking
import asyncio
from google import genai
from google.genai import types  # type: ignore
from config import GEMINI_KEY
from ai.sysPrompt import SYSTEM_PROMPT
from utils.logger import get_logger

# Initialize logger
logger = get_logger("ai", "logs/submissions/ai.log")

# Dictionary to store conversation history for each user
user_contexts = {}

async def generate(user_id: str, code: str, question: str):
    """Runs AI request asynchronously in a separate thread."""
    return await asyncio.to_thread(_generate_sync, user_id, code, question)

def _generate_sync(user_id: str, code: str, question: str):
    """Handles AI response generation in a thread-safe manner."""
    client = genai.Client(api_key=GEMINI_KEY)
    request_id = str(uuid.uuid4())  # Unique ID for tracking
    request_timestamp = time.time()  # Log when the request was made

    # Maintain user-specific conversation history
    if user_id not in user_contexts:
        user_contexts[user_id] = []

    input_text = f"The question is: {question}\n\nThe code is:\n{code}, verify for the given question and also check for any errors."
    # Log request details
    logger.info(f"[{request_timestamp}] Request ID {request_id} - User {user_id}: {input_text}")

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=input_text)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=600,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT),
        ],
    )

    try:
        complete_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-lite",
            contents=contents,
            config=generate_content_config,
        ):
            complete_text += chunk.text

        
        # Maintain user-specific context and trim old messages
        user_contexts[user_id].append({"role": "user", "content": input_text})
        user_contexts[user_id].append({"role": "assistant", "content": complete_text})
        user_contexts[user_id] = user_contexts[user_id][-5:]  # Keep last 5 messages
        # Log request details
        logger.info(f"[{request_timestamp}] Request ID {request_id} - Response for {user_id}: {complete_text}")
        return complete_text

    except Exception as e:
        logger.error(f"Error for {user_id} (Request ID: {request_id}) at [{request_timestamp}]: {e}")
        return "⚠️ AI validation failed. Please try again later!"