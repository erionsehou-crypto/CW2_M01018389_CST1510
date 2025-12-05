# ai_helper.py

import os
from openai import OpenAI

# Create OpenAI client using the API key from environment variable
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def ask_ai(question: str, context: str = "") -> str:
    """
    Ask the OpenAI API a question about the IT tickets.
    Optionally include a context string (summary of the data).
    """
    if not client.api_key:
        return "OpenAI API error: OPENAI_API_KEY environment variable is not set."

    # Build prompt
    system_message = (
        "You are an assistant that analyses IT support tickets. "
        "Use the provided data summary to give clear, concise, practical advice "
        "about trends, risks, workload and possible improvements."
    )

    # Merge question + context
    if context:
        user_content = (
            f"Data summary: {context}\n\n"
            f"User question: {question}"
        )
    else:
        user_content = question

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=400,
        )

        # For the new OpenAI client, content is in choices[0].message.content
        answer = response.choices[0].message.content
        if isinstance(answer, str):
            return answer.strip()
        else:
            # If content comes back as a list of parts, join them
            return "".join(part.get("text", "") for part in answer).strip()

    except Exception as e:
        # Always return a clean error message as a string
        return f"OpenAI API error: {type(e).__name__}: {e}"
