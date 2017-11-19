from telegram.ext import Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent
updater = Updater(token='[CENSORED]')
dispatcher = updater.dispatcher
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
	
def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
	
def caps(bot, update, args):
	text_caps = ' '.join(args).upper()
	bot.send_message(chat_id=update.message.chat_id, text=text_caps)	
	
def inline_caps(bot, update):
     query = update.inline_query.query
     if not query:
         return
     results = list()
     results.append(
         InlineQueryResultArticle(
             id=query.upper(),
             title='Caps',
             input_message_content=InputTextMessageContent(query.upper())
         )
     )
     bot.answer_inline_query(update.inline_query.id, results)



from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)

inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

#close with ctrl-c
updater.start_polling()
updater.idle()
