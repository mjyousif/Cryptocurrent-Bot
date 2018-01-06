from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, Message

#this stuff is for the webhook
import logging
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, MessageHandler, Filters

from uuid import uuid4
from json_api import *
from feedReader import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN='[CENSORED]'

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
            j=0
            for j in (range(len(newsQuery)-2)):
                newsQuery[1]=newsQuery[1]+' '+newsQuery[2]
                del newsQuery[2]
            newsArticles=news(newsQuery[1])
        results=[]
        i=0
        for i in range(len(newsArticles)):
            results.append(InlineQueryResultArticle(id=uuid4(),title=newsArticles[i].title,input_message_content=InputTextMessageContent(newsArticles[i].link),description=newsArticles[i].description,))
    elif ',' in query:
        classifiedQuery=classifyQuery(query)
        i=0
        jsonDataList=[]
        #this loop saves all the data in a list to be used in parallel to the coinQuery list
        for i in range(len(classifiedQuery.coinQuery)):
            jsonDataList.append(getCoinData(classifiedQuery.coinQuery[i],classifiedQuery.currency))
        #stuff that will go in the results, prepared up here because I can't do it in their respective results
        #Ternarys to remove things that wouldn't make sense in certain conditions. Like if the data is 'N/A', I don't want the currency to show
        #The big loop gets the data in a list which is joined however it needs to be in the results
        nameList=[]
        valueList=["Values:"]
        symbolValueList=[]
        capList=["Market Caps:"]
        symbolCapList=[]
        hourList=["1 Hour Changes:"]
        symbolHourList=[]
        dayList=["1 Day Changes:"]
        symbolDayList=[]
        weekList=["7 Day Changes:"]               
        symbolWeekList=[]
        k=0
        for k in range(len(classifiedQuery.coinQuery)):
            nameList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+")")  
            
            valueList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['price_'+classifiedQuery.currency.lower()]+" "+(classifiedQuery.currency.upper() if jsonDataList[k]['price_'+classifiedQuery.currency.lower()] !='N/A' else ""))
            symbolValueList.append(jsonDataList[k]['symbol']+": "+jsonDataList[k]['price_'+classifiedQuery.currency.lower()]+" "+(classifiedQuery.currency.upper() if jsonDataList[k]['price_'+classifiedQuery.currency.lower()] !='N/A' else "")) 
            
            capList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['market_cap_'+classifiedQuery.currency.lower()]+" "+(classifiedQuery.currency.upper() if jsonDataList[k]['market_cap_'+classifiedQuery.currency.lower()] !='N/A' else ""))
            symbolCapList.append(jsonDataList[k]['symbol']+": "+jsonDataList[k]['market_cap_'+classifiedQuery.currency.lower()]+" "+(classifiedQuery.currency.upper() if jsonDataList[k]['market_cap_'+classifiedQuery.currency.lower()] !='N/A' else ""))
            
            
            hourList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_1h']+"%")
            symbolHourList.append(jsonDataList[k]['symbol']+": "+jsonDataList[k]['percent_change_1h']+"%")
            
            dayList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_24h']+"%")
            symbolDayList.append(jsonDataList[k]['symbol']+": "+jsonDataList[k]['percent_change_24h']+"%")
            
            weekList.append(jsonDataList[k]['name']+" ("+jsonDataList[k]['symbol']+"): "+jsonDataList[k]['percent_change_7d']+"%")
            symbolWeekList.append(jsonDataList[k]['symbol']+": "+jsonDataList[k]['percent_change_7d']+"%")
        
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=', '.join(nameList),
                input_message_content=InputTextMessageContent('\n'.join(nameList)),
                thumb_url='https://coinmarketcap.com/static/img/CoinMarketCap.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=classifiedQuery.currency.upper()+' Values',
                description='|'.join(symbolValueList),
                input_message_content=InputTextMessageContent('\n'.join(valueList)),
                thumb_url='https://i.imgur.com/My7IG7r.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=classifiedQuery.currency.upper()+' Market Capitalizations',
                description='|'.join(symbolCapList),
                input_message_content=InputTextMessageContent('\n'.join(capList)),
                thumb_url='https://i.imgur.com/egncB1b.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Changes",
                description='|'.join(symbolHourList),
                input_message_content=InputTextMessageContent('\n'.join(hourList)),
                thumb_url='https://i.imgur.com/pza5Xjb.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Changes",
                description='|'.join(symbolDayList),
                input_message_content=InputTextMessageContent('\n'.join(dayList)),
                thumb_url='https://i.imgur.com/98YM0PA.png'
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Changes",
                description='|'.join(symbolWeekList),
                input_message_content=InputTextMessageContent('\n'.join(weekList)),
                thumb_url='https://i.imgur.com/ZbPOM53.png'
            ), 
            InlineQueryResultArticle(
                id=uuid4(),
                title='Summary of '+', '.join(nameList),
                input_message_content=InputTextMessageContent(
                    '\n'.join(valueList)+'\n\n'+
                    '\n'.join(capList)+'\n\n'+
                    '\n'.join(hourList)+'\n\n'+
                    '\n'.join(dayList)+'\n\n'+
                    '\n'.join(weekList)+'\n\n'
                    ),
                thumb_url='https://i.imgur.com/t6BPcMR.png'
            ),            
        ]
    elif "/" in query:
        #Format the query to remove spaces that would mess up format
        query=query.replace(' /','/')
        query=query.replace('/ ','/')
        query=query.replace(' ','-')
        coinList=query.split('/')
        coin1Data=getCoinData(coinList[0],'usd')
        coin2Data=getCoinData(coinList[1],'usd')
        coin1Name=coin1Data['name']
        coin1Symbol=coin1Data['symbol']
        coin1Value=coin1Data['price_usd']
        coin2Name=coin2Data['name']
        coin2Symbol=coin2Data['symbol']
        coin2Value=coin2Data['price_usd']
        #If the value for the coin is not available, return none so that nothing is returned to the user.
        if coin1Value=='N/A' or coin2Value=='N/A':
            coin1InCoin2=None
        #Do some manipulation. Turn the string from the data into float to do the math to get the value and return to string. Limit the value to 8 places past the decimal. Comma separate the left side of the number.
        else:
            coin1InCoin2=str(float(coin1Value.replace(',',''))/float(coin2Value.replace(',','')))
            coin1InCoin2=coin1InCoin2[:coin1InCoin2.find('.')+9]
            coin1InCoin2="{:,}".format(float(coin1InCoin2[:coin1InCoin2.find('.')]+'.'+coin1InCoin2[coin1InCoin2.find('.')+1:]))

        results=[
            InlineQueryResultArticle(
                id=uuid4(),
                title=coin1Name+' ('+coin1Symbol+') / '+coin2Name+' ('+coin2Symbol+')',
                description=coin1InCoin2+' '+coin1Symbol+'/'+coin2Symbol,
                input_message_content=InputTextMessageContent(coin1InCoin2+' '+coin1Name+' ('+coin1Symbol+') / '+coin2Name+' ('+coin2Symbol+')'),
                thumb_url='https://i.imgur.com/My7IG7r.png'
            ),
        ]
        
    else:
        #puts the query into a class that stores the coin and the currency
        classifiedQuery=classifyQuery(query)
        coinData=getCoinData(classifiedQuery.coinQuery[0],classifiedQuery.currency)
        coinName=coinData['name']
        coinSymbol=coinData['symbol']
        coinPrice=coinData['price_'+classifiedQuery.currency]+" "+(classifiedQuery.currency.upper() if coinData['price_'+classifiedQuery.currency.lower()] !='N/A' else "")
        coinCap=coinData['market_cap_'+classifiedQuery.currency]+" "+(classifiedQuery.currency.upper() if coinData['market_cap_'+classifiedQuery.currency.lower()] !='N/A' else "")
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

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(InlineQueryHandler(inline_crypto))
        
        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()
    
# def main():
    # updater = Updater(token='491978101:AAEJLq5HTtDH-9l4PCPj9Fu2O9FRapGhWV8')
    # dp=updater.dispatcher
    
    # #commands to answer
    # dp.add_handler(CommandHandler('start', start))
    
    # #non commands
    # dp.add_handler(InlineQueryHandler(inline_crypto))
    
    # #log errors
    # dp.add_error_handler(error)
    
    # #start bot

    # updater.start_polling()
    # #close with ctrl-c
    # updater.idle()
        
    

if __name__=='__main__':
    setup()