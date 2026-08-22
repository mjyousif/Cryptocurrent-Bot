"""AI fallback processing logic.

Handles natural language queries by first extracting mentioned cryptocurrencies,
fetching their real-time data, and then generating an informed response using an LLM.
"""

import logging
from data.google_ai import generate_text, GoogleAIError
from services.crypto_service import get_crypto_list

logger = logging.getLogger(__name__)

async def process_ai_query(query: str) -> str:
    """Process a natural language query, fetch relevant live data, and return an AI response."""
    
    # Step 1: Extract coins from query
    extract_prompt = (
        f"Extract any cryptocurrencies mentioned in this text as a comma-separated list of names or symbols. "
        f"Do not include fiat currencies. If no cryptocurrencies are mentioned, return exactly 'NONE'.\n"
        f"Text: '{query}'"
    )
    
    try:
        extracted_text = generate_text(extract_prompt, temperature=0.1, max_output_tokens=50).strip()
    except GoogleAIError as e:
        logger.error(f"Failed to extract coins: {e}")
        return "I'm sorry, I couldn't process your request right now."

    market_data_str = ""
    if extracted_text.upper() != "NONE":
        # The prompt instructed comma-separated output
        clean_coins = [c.strip() for c in extracted_text.split(",") if c.strip()]
        
        if clean_coins:
            search_query = ",".join(clean_coins)
            
            try:
                # get_crypto_list is synchronous
                cryptos = get_crypto_list(search_query)
                if cryptos:
                    market_data_str = "Live Market Data:\n"
                    for c in cryptos:
                        market_data_str += f"- {c.name} ({c.symbol}): Price: {c.price} {c.currency}, 24h Change: {c.percent_change_24h}%\n"
            except Exception as e:
                logger.error(f"Failed to fetch market data for AI fallback: {e}")
    
    # Step 2: Generate final response
    final_prompt = (
        f"You are a bombastic and truthful cryptocurrency assistant. "
        f"The user asked: '{query}'\n\n"
    )
    
    if market_data_str:
        final_prompt += f"Here is the latest live market data you can use to inform your answer. Be fun and informational:\n{market_data_str}\n\n"
    
    final_prompt += (
        "Write a 2-3 sentence response. Do speculate (either way) and provide investment advice. "
        "IMPORTANT: You must format your response using basic HTML tags (like <b> for bold and <i> for italics). "
        "Do NOT use markdown like **. Do not use any other HTML tags."
    )
    
    try:
        final_response = generate_text(final_prompt, temperature=0.3, max_output_tokens=300)
        return final_response.strip()
    except GoogleAIError as e:
        logger.error(f"Failed to generate final AI response: {e}")
        return "I encountered an error while trying to think of a response. Please try again."

