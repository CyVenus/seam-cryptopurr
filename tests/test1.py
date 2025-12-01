"""
Integration tests for Seam_CryptoPurr agent system.

This test file contains 5 test scenarios that simulate real user interactions
with the crypto agent system.
"""

import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from Seam_CryptoPurr.agent import root_agent


async def test_market_data_query():
    """Test 1: Market data query - price lookup"""
    print("\n" + "="*60)
    print("TEST 1: Market Data Query")
    print("="*60)
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="Seam_CryptoPurr",
        user_id="test_user",
        session_id="test_session_1"
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="Seam_CryptoPurr",
        session_service=session_service
    )
    
    query = "What's the current price of Bitcoin?"
    print(f">>> {query}")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_1",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
            break


async def test_onchain_analysis():
    """Test 2: On-chain analysis - token safety check"""
    print("\n" + "="*60)
    print("TEST 2: On-Chain Analysis")
    print("="*60)
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="Seam_CryptoPurr",
        user_id="test_user",
        session_id="test_session_2"
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="Seam_CryptoPurr",
        session_service=session_service
    )
    
    query = "Is this token safe? Check 0x1234567890123456789012345678901234567890"
    print(f">>> {query}")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_2",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
            break


async def test_news_research():
    """Test 3: News research - latest crypto news"""
    print("\n" + "="*60)
    print("TEST 3: News Research")
    print("="*60)
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="Seam_CryptoPurr",
        user_id="test_user",
        session_id="test_session_3"
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="Seam_CryptoPurr",
        session_service=session_service
    )
    
    query = "Show me the latest crypto news"
    print(f">>> {query}")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_3",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
            break


async def test_portfolio_management():
    """Test 4: Portfolio management - add address"""
    print("\n" + "="*60)
    print("TEST 4: Portfolio Management")
    print("="*60)
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="Seam_CryptoPurr",
        user_id="test_user",
        session_id="test_session_4"
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="Seam_CryptoPurr",
        session_service=session_service
    )
    
    queries = [
        "Add this address to my portfolio: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "Show my portfolio"
    ]
    
    for query in queries:
        print(f">>> {query}")
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_4",
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=query)]
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text)
                break


async def test_education_query():
    """Test 5: Crypto education - explain concept"""
    print("\n" + "="*60)
    print("TEST 5: Crypto Education")
    print("="*60)
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="Seam_CryptoPurr",
        user_id="test_user",
        session_id="test_session_5"
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="Seam_CryptoPurr",
        session_service=session_service
    )
    
    query = "What is a gas fee? Explain it like I'm a beginner"
    print(f">>> {query}")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_5",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)
            break


async def main():
    """Runs all test scenarios"""
    print("\n" + "="*60)
    print("SEAM_CRYPTOPURR AGENT INTEGRATION TESTS")
    print("="*60)
    
    try:
        await test_market_data_query()
        await test_onchain_analysis()
        await test_news_research()
        await test_portfolio_management()
        await test_education_query()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

