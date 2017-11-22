from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, Message

from uuid import uuid4
from json_api import *



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
		 InlineQueryResultPhoto(
             id=uuid4(),
			 photo_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+getCoinID(query) +'.png'),
			 thumb_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+getCoinID(query) +'.png'),
             thumb_width=512,
			 # title='Summary2'#,
             # caption=summary(query)
		 ),
         InlineQueryResultArticle(
             id=uuid4(),
             title='USD Value',
             input_message_content=InputTextMessageContent(cryptoValueMain(query)),
			 thumb_url=None,
			 #thumb_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+getCoinID(query) +'.png')
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

	 
def main():
	updater = Updater(token='460892339:AAGDPHRipffdOM8AR7IXdsUoMpnIsoSJwFw')
	dp=updater.dispatcher
	
	#commands to answer
	dp.add_handler(CommandHandler('start', start))
	
	#non commands
	dp.add_handler(InlineQueryHandler(inline_crypto))



	#start bot
	updater.start_polling()
	#close with ctrl-c
	updater.idle()
	
if __name__=='__main__':
	main()