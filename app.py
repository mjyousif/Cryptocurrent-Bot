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
        for i in range(len(newsArticles)):
            results.append(InlineQueryResultArticle(id=uuid4(),title=newsArticles[i].title,input_message_content=InputTextMessageContent(newsArticles[i].link),description=newsArticles[i].description,))
    if ',' in query:
        classifiedQuery=classifyQuery(query)
        i=0
        jsonDataList=[]
        #this loop saves all the data in a list to be used in parallel to the coinQuery list
        for i in range(len(classifiedQuery.coinQuery)):
            jsonDataList.append(getCoinData(classifiedQuery.coinQuery[i],classifiedQuery.currency))
        #stuff that will go in the results, prepared up here because I can't do it in their respective results
        nameList=""
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            nameList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"), \n"  
        valueList="Values:\n"
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            valueList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['price_'+classifiedQuery.currency.lower()]+" "+classifiedQuery.currency.upper()+"\n" 
        capList="Market Caps:\n"
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            capList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['market_cap_'+classifiedQuery.currency.lower()]+" "+classifiedQuery.currency.upper()+"\n" 
        hourList="1 Hour Changes:\n"
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            hourList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_1h']+"%"+"\n"  
        dayList="1 Day Changes:\n"
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            dayList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_24h']+"%"+"\n"  
        weekList="7 Day Changes:\n"
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            weekList+=jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_7d']+"%"+"\n"           
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=nameList,
                input_message_content=InputTextMessageContent(nameList),
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Values',
                input_message_content=InputTextMessageContent(valueList),
                thumb_url='https://i.imgur.com/My7IG7r.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Market Capitalizations',
                input_message_content=InputTextMessageContent(capList),
                thumb_url='https://i.imgur.com/egncB1b.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Changes",
                input_message_content=InputTextMessageContent(hourList),
                thumb_url='https://i.imgur.com/pza5Xjb.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Changes",
                input_message_content=InputTextMessageContent(dayList),
                thumb_url='https://i.imgur.com/98YM0PA.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Changes",
                input_message_content=InputTextMessageContent(weekList),
                thumb_url='https://i.imgur.com/ZbPOM53.png'
            ),   
        ]
    
    else:
        classifiedQuery=classifyQuery(query)
        coinData=getCoinData(classifiedQuery.coinQuery[0],classifiedQuery.currency)
        coinName=coinData['name']
        coinSymbol=coinData['symbol']
        coinPrice=coinData['price_'+classifiedQuery.currency]+" "+classifiedQuery.currency.upper()
        coinCap=coinData['market_cap_'+classifiedQuery.currency]+" "+classifiedQuery.currency.upper()
        coin1hr=coinData['percent_change_1h']+"%"
        coin1day=coinData['percent_change_24h']+"%"
        coin7day=coinData['percent_change_7d']+"%"
        results = [
            InlineQueryResultPhoto(
                id=uuid4(),
                photo_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+coinData['id'] +'.png'),
                thumb_url=('https://files.coinmarketcap.com/static/img/coins/128x128/'+coinData['id'] +'.png'),
                title=coinData['name']+'('+coinSymbol+')',
                caption=coinData['name']+' ('+coinSymbol+')',
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Value: '+coinPrice,
                input_message_content=InputTextMessageContent(coinName+': '+coinPrice),
                thumb_url='https://i.imgur.com/My7IG7r.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title='Market Capitalization: '+coinCap,
                input_message_content=InputTextMessageContent(coinName+' Market Capitalization: '+coinCap),
                thumb_url='https://i.imgur.com/egncB1b.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Change: "+coin1hr,
                input_message_content=InputTextMessageContent(coinName+' One Hour Change: '+coin1hr),
                thumb_url='https://i.imgur.com/pza5Xjb.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Change: "+coin1day,
                input_message_content=InputTextMessageContent(coinName+' One Day Change: '+coin1day),
                thumb_url='https://i.imgur.com/98YM0PA.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Change: "+coin7day,
                input_message_content=InputTextMessageContent(coinName+' Seven Day Change: '+coin7day),
                thumb_url='https://i.imgur.com/ZbPOM53.png'
            ),    
            InlineQueryResultArticle(
                id=uuid4(),
                title='Summary of '+coinName+'('+coinSymbol+')',
                input_message_content=InputTextMessageContent(
                    "---"+coinName+" Summary"+'('+coinSymbol+')'+"---"+
                    "\nPrice: "+coinPrice+
                    "\nMarket Capitalization: "+coinCap+
                    "\n1 hour percent change: "+coin1hr+
                    "\n24 hour percent change: "+coin1day+
                    "\n7 day percent change: "+coin7day),
                thumb_url='https://i.imgur.com/t6BPcMR.png'
            ),
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