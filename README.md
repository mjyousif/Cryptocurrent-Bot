# CryptoCurrent
This is a telegram bot that gets information about cryptocurrencies and provides it inline to the user. 

In order to use this bot, open Telegram and type @CryptoCurrent_bot, you will then have a few options.

### Crypto Currency Information

##### Single Coin
In order to get current information about a coin, enter the following

`<@CryptoCurrent_bot <crypto currency name or symbol> [currency symbol]>`

For the crypto currency name or symbol, you could enter something like "Bitcoin" or "btc". Case does not matter. It should also accept spaces, so a currency such as "Bitcoin Cash" or "bch" will work the same.

For the currency symbol, you could enter a desired output currency. If the currency is one of the accepted currencies, it will provide the information in that currency.
The following are acceptted currencies:
>["AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR", "USD"]

##### Multi Coin

`<@CryptoCurrent_bot <coin-1>,<coin-2>,...<coin-n> [currency symbol]>`

This functionality allows the user to get information about several coins in one messages, allowing quick comparison of any of the available informations in a single message. Any of the tokens can be the name or symbol of the coin. Theoretically, the user can enter as many coins as desired, perhaps limitted by timeout. The coins must be separated by a comma.

If the user so desires, they can enter a currency code from the above list of accepted currencies and get the information in that currency.

All information for this functionality is retrieved from https://api.coinmarketcap.com/v1/ticker/

### Crypto Currency News
In order to view news about crypto currencies, enter the following

`<@CryptoCurrent_bot news [tag]>`

Without entering a tag, the bot will display the top 5 articles it retrieved. 

Entering a tag will provide up to 5 articles that are tagged with that word. For example, one might enter "bitcoin" and the results will be ones tagged with "Bitcoin". Case does not matter.

All information for this functionality is retrieved from https://www.coindesk.com/feed/

## Credits

Thanks to Telegram for enabling creators on their platform by having the bot api.

Thanks to the python-telegram-bot team for creating a telegram bot api in python.

Thanks to my TOP COUNSEL Izan Mubarak who accompanied me in the learning process and provided top tier expertise.

Thanks to the RedHat OpenShift program which allows me to host my program online.
