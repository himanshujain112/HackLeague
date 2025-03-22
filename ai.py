import base64
from google import genai
from google.genai import types # type: ignore
from config import GEMINI_KEY

def generate(input_text: str):
    client = genai.Client(
        api_key=GEMINI_KEY,
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
        max_output_tokens=600,  # Assuming an average of 2 tokens per word
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Generate a code snippet based on the given text. Do not include the input text in the output, make it short and answer."""),
        ],
    )

    complete_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        complete_text += chunk.text
        print(chunk.text, end="")
    
    return complete_text