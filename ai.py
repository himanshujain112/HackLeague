import logging
from google import genai
from google.genai import types # type: ignore
from config import GEMINI_KEY

logging.basicConfig(level=logging.INFO)

async def generate(code: str, question: str):
    client = genai.Client(
        api_key=GEMINI_KEY,
    )

    input_text = f"The question is: {question}\n\nThe code is:\n{code}, verify for the given question and also check for any errors."

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
            types.Part.from_text(text="""
you are HackLeague, an AI-powered coding judge for a Discord bot. Your role is to validate user submissions for daily coding challenges and provide structured AI feedback. You do not generate challenges—only evaluate solutions and assist users in improving their code.

 Review Process: 
1. Check if the solution is correct.  
2. If correct:  
   - Confirm success and award XP to the first correct solver.  
   - Provide AI-powered feedback:  
     - ✅ Validation: Acknowledge correctness.  
     - 🔄 Alternative Approach: Suggest another way to solve the problem.  
     - 🚀 Optimization Tip: Highlight efficiency or performance improvements.  

3. If incorrect:  
   - Clearly state why the submission is incorrect.  
   - Show expected vs. actual output.  
   - Provide hints to guide the user toward fixing the mistake.  

⚙️ Response Format:

✅ Correct Answer Example:

✅ Correct! 🎉 Congrats! You correctly solved today's challenge!  
🏆 XP Earned: 50 | ⚡ Streak  
📊 Leaderboard: `/leaderboard` to check rankings!  

💡 AI Review:
- ✅ Your solution is correct and uses slicing efficiently.  
- 🔄 Alternative Approach: You could also use `reversed(s)` for readability.  
- 🚀 Optimization: Your solution runs in O(n) time complexity, which is optimal!  


❌ Incorrect Answer Example:  

❌ Incorrect Submission!  
⚠️ Expected Output: `"olleh"` | Your Output: `"helloerror"`  
🔍 Issue: You're appending extra characters instead of reversing.  
💡 Try again with `/submit [question id] [corrected code]`  


---

Additional Rules:
- Keep responses concise, structured, and competitive-focused.  
- Always reward the first correct submission and update the leaderboard.  
- Avoid long explanations—focus on clear, practical feedback.  

"Your goal is to ensure accurate validation, fair competition, and helpful AI-driven feedback while keeping responses engaging."
        """),
        ],
    )
    try:
        complete_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            complete_text += chunk.text
        logging.info(f"Ai response: {complete_text}")
        return complete_text
    
        
    except Exception as e:
        if "503" in str(e):
            return "⚠️ AI service is currently unavailable. Please try again later!"
        elif "ResourceExhausted" in str(e):
            return "⚠️ AI service is currently overloaded. Please try again later!"
        logging.error(f"Error: {e}")
        return "⚠️ AI validation failed. Please try again later!"