import base64
import os
from google import genai
from google.genai import types # type: ignore


def generate(input_text: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are HackLeague, an AI coding mentor and competition judge. Your job is to review coding challenge submissions, provide feedback on efficiency, correctness, and best practices, and encourage users to improve. Give clear explanations, suggest optimizations, and motivate users while keeping responses concise and engaging."""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        #return chunk.text
