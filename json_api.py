import requests
#------------------------------------------------------------------
#Misc. functions for use here
#comma separated numbers that are entered as strings
#keeps precision of the numbers
def prettyANDprecise(strNum):
	numStrSplit=(strNum.split('.',1))
	numStrFormatLeft="{:,}".format(float(numStrSplit[0]))
	numStrFormatLeft=(numStrFormatLeft.split('.',1))
	if (len(numStrSplit)==1):
		pApOutput=numStrFormatLeft[0]
	else:
		pApOutput=(str(numStrFormatLeft[0])+'.'+numStrSplit[1])
	return pApOutput

#-------------------------------------------------------------------
#Function to get the json for the coin
def getCoinData(coin):
	main_api='https://api.coinmarketcap.com/v1/ticker/'
	coin=coin.replace(" ","-")
	url=main_api+coin
	json_data_end=requests.get(url).json() 
	if 'error' in json_data_end: #This will check if the entered name exists, if not, check if the symbol exists
		url='https://api.coinmarketcap.com/v1/ticker/?limit=10000'
		json_data=requests.get(url).json()
		index=0
		for index in range(len(json_data)): #loops through entire coinmarketcap ticker until symbol found
			if coin.upper()==json_data[index]["symbol"]:
				json_data_end=json_data[index]
				break	

	#the result will depend on whether the input was name or symbol
	#The dimensions of the json change depending on that
	#the try-except is to overcome that because that's the first thing i thought of
	try:
		json_data_end=json_data_end[0]
	except:
		json_data_end=json_data_end
		

	#this gets values with comma separations and makes sure that the data exists. if there is null data, replace with "N/A"
	if (json_data_end['price_usd']==None):
		json_data_end['price_usd']='N/A'
	else:
		json_data_end['price_usd']=prettyANDprecise(json_data_end['price_usd'])
	
	if (json_data_end['market_cap_usd']==None):
		json_data_end['market_cap_usd']='N/A'
	else:
		json_data_end['market_cap_usd']=prettyANDprecise(json_data_end['market_cap_usd'])
	
	#coinmarketcap info has a decimal at the end of market cap for some reason. this gets rid of that
	json_data_end['market_cap_usd']=json_data_end['market_cap_usd'].split('.')
	json_data_end['market_cap_usd']=json_data_end['market_cap_usd'][0]
		
		
		
	if (json_data_end['24h_volume_usd']==None):
		json_data_end['24h_volume_usd']='N/A'
	else:		
		json_data_end['24h_volume_usd']=prettyANDprecise(json_data_end['24h_volume_usd'])
	
	if(json_data_end['percent_change_1h']==None):
		json_data_end['percent_change_1h']='?'
	if(json_data_end['percent_change_24h']==None):
		json_data_end['percent_change_24h']='?'
	if(json_data_end['percent_change_7d']==None):
		json_data_end['percent_change_7d']='?'
	
	return json_data_end
	
	#function to get coin id
def getCoinID(coin):
	coinData=getCoinData(coin)
	coinID=coinData['id']
	return coinID


#----------------------------------------------------------------------

#Function to get market cap
def cryptoMarketCap(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	marketCap=coinData['market_cap_usd']	
	marketCapOutput=(name+' market capitalization: $'+marketCap)
	return marketCapOutput

	#Function to get crypto value
def cryptoValueMain(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']		
	valueOutput=(name+': $'+priceUSD)
	return valueOutput

	#function gets percent change in 1 hour
def oneHourChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange1hr=coinData['percent_change_1h']
#	dollarChange1hr=float(priceUSD)/(1+float(pctChange1hr)/100)
	oneHourChangeOutput=(name+" 1 hour percent change: "+pctChange1hr+"%")
	return oneHourChangeOutput

	#function gets percent change in 24 hour
def oneDayChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange24hr=coinData['percent_change_24h']
	oneDayChangeOutput=(name+" 24 hour percent change: "+pctChange24hr+"%")	
	return oneDayChangeOutput

	#function gets percent change in 7 days
def sevenDayChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange7d=coinData['percent_change_7d']
	sevenDayChangeOutput=(name+" 7 day percent change: "+pctChange7d+"%")		
	return sevenDayChangeOutput
	
	#function presents all all the above data in one string
def summary(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	marketCap=coinData['market_cap_usd']
	priceUSD=coinData['price_usd']	
	pctChange1hr=coinData['percent_change_1h']
	pctChange24hr=coinData['percent_change_24h']
	pctChange7d=coinData['percent_change_7d']
	summaryOutput=("---"+name+" Summary---"+
		"\nPrice USD: $"+priceUSD+
		"\nMarket Capitalization: $"+marketCap+
		"\n1 hour percent change: "+pctChange1hr+"%"+
		"\n24 hour percent change: "+pctChange24hr+"%"+
		"\n7 day percent change: "+pctChange7d+"%")
	return summaryOutput
