from telegram.ext import Updater, CommandHandler
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, Message

from uuid import uuid4
from json_api import *

updater = Updater(token='491978101:AAEM4E-DMKblOLwxvbkO6XOMhoXgwRATvVs')
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
	bot.send_message(
					chat_id=update.message.chat_id, 
					text=('Use me inline by tagging me and typing a crypto currency!')
					)
	
def inline_crypto(bot, update):
     query = update.inline_query.query
     if not query:
         return
     results = [
         InlineQueryResultArticle(
             id=uuid4(),
             title='USD Value',
             input_message_content=InputTextMessageContent(cryptoValueMain(query))
         ),
		 InlineQueryResultArticle(
             id=uuid4(),
             title='Market Capitalization',
             input_message_content=InputTextMessageContent(cryptoMarketCap(query))
         ),
		 InlineQueryResultArticle(
             id=uuid4(),
             title='1 hour change',
             input_message_content=InputTextMessageContent(oneHourChange(query))
         ),
		 InlineQueryResultArticle(
             id=uuid4(),
             title='24 hour change',
             input_message_content=InputTextMessageContent(oneDayChange(query))
         ),
		 InlineQueryResultArticle(
             id=uuid4(),
             title='7 day change',
             input_message_content=InputTextMessageContent(sevenDayChange(query))
         ),	
		 InlineQueryResultArticle(
             id=uuid4(),
             title='Summary',
             input_message_content=InputTextMessageContent(summary(query))
         )	
     ]
     bot.answer_inline_query(update.inline_query.id, results)	

	
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

inline_crypto_handler = InlineQueryHandler(inline_crypto)
dispatcher.add_handler(inline_crypto_handler)


#close with ctrl-c
updater.start_polling()
updater.idle()