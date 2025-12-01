import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from Seam_CryptoPurr.agent import root_agent
from google.genai import types as genai_types


async def main():
    """Runs the agent with a sample query."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )

    queries = [
        "What's the current price of Bitcoin?",
        "Show me the latest crypto news",
        "What is a gas fee? Explain it like I'm a beginner",
        "Show me a crypto meme",
        "Flip a coin for me",
    ]

    for query in queries:
        print(f">>> {query}")
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=genai_types.Content(
                role="user", 
                parts=[genai_types.Part.from_text(text=query)]
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())