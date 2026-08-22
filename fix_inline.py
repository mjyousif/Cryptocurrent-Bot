
import sys
import re

with open("api/inline_processor.py", "r") as f:
    content = f.read()

replacement = """        results = [
            InlineQueryResultArticle(
                id="ai_fallback",
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(f"Thinking about: {query} ??..."),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("? Generating...", callback_data="ignore")]
                ])
            )
        ]"""

content = re.sub(r"        results = \[\s*InlineQueryResultArticle\(\s*id=\"ai_fallback\",\s*title=title,\s*description=description,\s*input_message_content=InputTextMessageContent\(f\"Thinking about: \{query\} ??\.\.\.\"\),\s*\)\s*\]", replacement, content)

# ensure InlineKeyboardMarkup and InlineKeyboardButton are imported
if "InlineKeyboardMarkup" not in content:
    content = content.replace("from telegram import (", "from telegram import (\n    InlineKeyboardMarkup,\n    InlineKeyboardButton,")

with open("api/inline_processor.py", "w") as f:
    f.write(content)

