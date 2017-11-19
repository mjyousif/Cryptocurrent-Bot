def cryptoValue(coin):
	import requests

	main_api='https://api.coinmarketcap.com/v1/ticker/'

	#address='bitcoin'
	#coin=input('Enter a cryptocurrency: ')
	coin=coin.replace(" ","-")
	url=main_api+coin

	json_data=requests.get(url).json()
	#print(json_data)

	json_name=json_data[0]["name"]
	json_price=json_data[0]['price_usd']

	output= (json_name+': $'+json_price)
#	print (output)
	return output
	
#cryptoValue('bitcoin')