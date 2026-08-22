"""AI fallback processing logic.

Handles natural language queries by first extracting mentioned cryptocurrencies,
fetching their real-time data, and then generating an informed response using an LLM.
"""

import json
import logging

from data.google_ai import GoogleAIError, generate_text
from services.crypto_service import get_crypto_list
from services.feedReader import news

logger = logging.getLogger(__name__)


async def process_ai_query(query: str) -> str:
    """Process a natural language query, fetch relevant live data, and return an AI response."""

    # Step 1: Extract entities from query
    extract_prompt = (
        f"Extract any cryptocurrencies mentioned in this text (as names or symbols) and any "
        f"important news keywords or entities (like SEC, FED, regulations, people). "
        f"Return a JSON object with two keys: 'coins' and 'keywords', both being lists of strings.\n"
        f"Text: '{query}'"
    )

    try:
        extracted_text = generate_text(
            extract_prompt,
            temperature=0.1,
            max_output_tokens=150,
            response_format={"type": "json_object"},
        ).strip()
        data = json.loads(extracted_text)
        clean_coins = data.get("coins", [])
        keywords = data.get("keywords", [])
    except (GoogleAIError, json.JSONDecodeError) as e:
        logger.error(f"Failed to extract entities: {e}")
        return "I'm sorry, I couldn't process your request right now."

    market_data_str = ""
    news_data_str = ""

    if clean_coins:
        search_query = ",".join(clean_coins)
        try:
            cryptos = get_crypto_list(search_query)
            if cryptos:
                market_data_str = "Live Market Data:\n"
                for c in cryptos:
                    market_data_str += f"- {c.name} ({c.symbol}): Price: {c.price} {c.currency}, 24h Change: {c.percent_change_24h}%\n"
        except Exception as e:
            logger.error(f"Failed to fetch market data for AI fallback: {e}")

    combined_news_targets = clean_coins + keywords
    if combined_news_targets:
        try:
            for target in combined_news_targets:
                articles = news(target)
                if articles:
                    if not news_data_str:
                        news_data_str = "Recent News:\n"
                    news_data_str += f"- For {target}:\n"
                    for a in articles[:2]:
                        news_data_str += f"  * {a.title} - URL: {a.link}\n"
        except Exception as e:
            logger.error(f"Failed to fetch news data for AI fallback: {e}")

    # Step 2: Generate final response
    final_prompt = (
        f"You are a bombastic and truthful cryptocurrency assistant. "
        f"The user asked: '{query}'\n\n"
    )

    if market_data_str:
        final_prompt += f"Here is the latest live market data you can use to inform your answer. Be fun and informational:\n{market_data_str}\n\n"

    if news_data_str:
        final_prompt += f"Here is the latest news that might provide context for market movements:\n{news_data_str}\n\n"

    final_prompt += (
        "Write a 2-3 sentence response. Do speculate (either way) and provide investment advice. "
        "IMPORTANT: You must format your response using basic HTML tags (like <b> for bold and <i> for italics). "
        'If you use information from a news article, you MUST include a link to it using <a href="URL">Source</a>. '
        "Do not link to articles you don't use. Do NOT use markdown like **. Do not use any other HTML tags."
    )

    try:
        final_response = generate_text(
            final_prompt, temperature=0.3, max_output_tokens=300
        )
        return final_response.strip()
    except GoogleAIError as e:
        logger.error(f"Failed to generate final AI response: {e}")
        return "I encountered an error while trying to think of a response. Please try again."
