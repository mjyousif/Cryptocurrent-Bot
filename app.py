from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, Message

from uuid import uuid4
from json_api import *
from feedReader import *

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
    newsQuery=query.split(" ")
    if (newsQuery[0].lower()=="news"):
        if (len(newsQuery)==1):
            newsArticles=news()
        else:
            # newsArticles=news(newsQuery[1])
            j=0
            for j in (range(len(newsQuery)-2)):
                newsQuery[1]=newsQuery[1]+' '+newsQuery[2]
                del newsQuery[2]
            newsArticles=news(newsQuery[1])
        # newsArticles=news(None if len(newsQuery)==1 else newsQuery[1])
        results=[]
        i=0
        for i in range(len(newsArticles) if len(newsArticles)<5 else 5):
            results.append(InlineQueryResultArticle(id=uuid4(),title=newsArticles[i].title,input_message_content=InputTextMessageContent(newsArticles[i].link),description=newsArticles[i].description,))
    else:
        querySplitted=querySplit(query)
        coinData=getCoinData(query)
        coinName=coinData['name']
        results = [
            InlineQueryResultPhoto(
                id=uuid4(),
                photo_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+coinData['id'] +'.png'),
                thumb_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+coinData['id'] +'.png'),
                title=coinData['name']+'('+coinData['symbol']+')',
                caption=coinData['name']+' ('+coinData['symbol']+')',
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Value: '+cryptoValueMain(querySplitted, coinData),
                input_message_content=InputTextMessageContent(coinName+': '+cryptoValueMain(querySplitted, coinData)),
                thumb_url='https://i.imgur.com/My7IG7r.png'
                #thumb_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+getCoinID(query) +'.png')
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Market Capitalization: '+cryptoMarketCap(querySplitted, coinData),
                input_message_content=InputTextMessageContent(coinName+' Market Capitalization: '+cryptoMarketCap(querySplitted, coinData)),
                thumb_url='https://i.imgur.com/egncB1b.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=oneHourChange(coinData),
                input_message_content=InputTextMessageContent(coinName+' '+oneHourChange(coinData)),
                thumb_url='https://i.imgur.com/pza5Xjb.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=oneDayChange(coinData),
                input_message_content=InputTextMessageContent(coinName+' '+oneDayChange(coinData)),
                thumb_url='https://i.imgur.com/98YM0PA.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=sevenDayChange(coinData),
                input_message_content=InputTextMessageContent(coinName+' '+sevenDayChange(coinData)),
                thumb_url='https://i.imgur.com/ZbPOM53.png'
            ),    
            InlineQueryResultArticle(
                id=uuid4(),
                title='Summary of '+coinName,
                input_message_content=InputTextMessageContent(summary(querySplitted, coinData)),
                thumb_url='https://i.imgur.com/t6BPcMR.png'
            )
        ]
    bot.answer_inline_query(update.inline_query.id, results)    

     
def main():
    updater = Updater(token='[CENSORED]')
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