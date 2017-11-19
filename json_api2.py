import requests

def cryptoValue(coin):


	main_api='https://api.coinmarketcap.com/v1/ticker/'

	#address='bitcoin'
	#coin=input('Enter a cryptocurrency: ')
	coin=coin.replace(" ","-")
	url=main_api+coin

	json_data=requests.get(url).json()
	#print(json_data)
	#print (len(json_data[0]))
	if 'error' in json_data:
		output='INVALID'
	else:
		json_name=json_data[0]["name"]
		json_price=json_data[0]['price_usd']
		output= (json_name+': $'+json_price)
#	print (output)
	return output
	
#cryptoValue('bitcoin')
def cryptoValueShort(coin):
	main_api='https://api.coinmarketcap.com/v1/ticker/'
	url=main_api
	json_data=requests.get(url).json()
	index=0
	output='INVALID2'
	for index in range(len(json_data)):
		if coin.upper()==json_data[index]["symbol"]:
			json_name=json_data[index]["name"]
			json_price=json_data[index]['price_usd']
			output= (json_name+': $'+json_price)
			index==len(json_data)	
	return output
	
coinIn=input("Enter coin: ") #get the coin

inValue=cryptoValue(coinIn)
if inValue=='INVALID':
	inValue=cryptoValueShort(coinIn)

print(inValue)