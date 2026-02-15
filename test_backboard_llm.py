# Install: pip install backboard-sdk
import asyncio
import os
from backboard import BackboardClient

API_KEY = "espr_qvYnYNHmkKs7IeawnSVXZjqjiXE2TEGcEniXkDQ-d_Q"

async def main():
    if not API_KEY:
        raise RuntimeError("Set BACKBOARD_API_KEY environment variable")

    client = BackboardClient(api_key=API_KEY)

    # Create an assistant WITH WEB SEARCH ENABLED
    assistant = await client.create_assistant(
        name="Web Search Assistant",
        capabilities={
            "web_search": True
        }
    )

    # Create a thread
    thread = await client.create_thread(assistant.assistant_id)

    # Web-grounded query
    prompt = (
        "Search the web and summarize the latest benchmarks "
        "for disaster damage detection models in 2025."
    )

    response = await client.add_message(
        thread_id=thread.thread_id,
        content=[
    {"role": "system", "content": """You are a factual assistant. 
            Use web search when the user asks about current or real-world information. 
            Cite sources when possible."""},
    {"role": "user", "content": prompt}
]
,
        llm_provider="openai",   # backboard will still route search internally
        model_name="gpt-4o",
        stream=False
    )

    print("\n=== GROUNDED RESPONSE ===\n")
    print(response.content)

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
