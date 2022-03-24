from configparser import ConfigParser
import requests
import Classes
import datetime
import Setups
import hmac
import hashlib
import signal
import pandas as pd
import logging
import botslib.bots_api as ba


symbol = "ETHUSDT"
recvWindow = 1000000
quantity = 0.025

log = logging.basicConfig(filename='./logs/{}_Double_Soldiers.log'.format(symbol),
                            filemode='a',
                            level=logging.INFO,
                            format='%(asctime)s | %(levelname)s | %(message)s')


def quit_gracefully(*args):

    logging.info('----------------------------------')
    logging.info('Logic to kill the robot initialize!')
    logging.info('----------------------------------')
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)

parser = ConfigParser()
parser.read('./config.ini')

#Functions for get the Signature to send on Request
def hashing(query_string, secret_key):
    return hmac.new(secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

#Function to calculate the timestamp on microseconds
def timestamp():
    return int(datetime.datetime.now().timestamp())*1000

#API KEY from market data real account
api_key_md = parser.get("API_MARKET_DATA","api_key").strip('"\'')
api_secret_md = parser.get("API_MARKET_DATA","secret_key").strip('"\'')

#Read config files which have URLs and Keys from Testnet from Binance
api_key = parser.get("API_KEY_ROBOS","api_key").strip('"\'')
api_secret = parser.get("API_KEY_ROBOS","secret_key").strip('"\'')
url_futures = parser.get("API_KEY_ROBOS","url_futures").strip('"\'')
url_create_orders = parser.get("API_KEY_ROBOS","create_orders").strip('"\'')
url_positions = parser.get("API_KEY_ROBOS","position").strip('"\'')

# get headers
headers = Classes.API_KEY(api_key,api_secret).get_headers()

#Classes to control the positions with getters and setters
position = Classes.Position()

#Positions of Binance URLs and create new orders
url = url_futures+url_positions
url_post = url_futures+url_create_orders


get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers).json()

logging.info('---------------------------------------')
logging.info('BOT INITIALIZED!!')
logging.info('Datetime: %s', datetime.datetime.now().strftime('%H:%M:%S:%f'))
logging.info('---------------------------------------')


logging.info("------------------------------")
logging.info("SEARCH FOR POSITIONS...")
logging.info("------------------------------")

for i in get_positions:

    if float(i['positionAmt']) == 0:
        logging.info("------------------------------")
        logging.info("NO POSITIONS")
        logging.info("------------------------------")


    #If is Long Position opened
    elif float(i['positionAmt']) > 0:

        logging.info("------------------------------")
        logging.info("LONG POSITION OPENED")
        logging.info("------------------------------")


    #If is Short Position opened
    elif float(i['positionAmt']) < 0:

        logging.info("------------------------------")
        logging.info("SHORT POSITION OPENED")
        logging.info("------------------------------")


while True:
    
    try:
        
        seconds = datetime.datetime.now().second
        delta_sec = 60 - seconds % 60

        if delta_sec == 60:

            try: 
                get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers)

                if get_positions is not None:
                    
                    get_positions = get_positions.json()

                    for i in get_positions:

                        #No position
                        if float(i['positionAmt']) == 0:
                            position.LongOpened = False
                            position.ShortOpened = False

                            double_soldiers = Setups.Double_Soldiers_Strategy("{}".format(symbol),"1h").get_signal(api_key_md,api_secret_md)

                            if double_soldiers == "buy":

                                side = "BUY"
                                type = "MARKET"

                                data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
                                                    .format(symbol,side,type,quantity,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
                                                    .format(symbol,side,type,quantity,recvWindow,timestamp()), api_secret)), headers=headers).json()

                                # logging.info(data)

                                get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers).json()
                                # logging.info(get_positions)

                                logging.info("-----------------------------------------")
                                logging.info("Long position opened")
                                logging.info("Symbol: %s",data['symbol'])
                                logging.info("Type: %s",data['type'])
                                logging.info("Price:%s", get_positions[0]['entryPrice'])
                                logging.info("Volume:%s",data['origQty'])
                                logging.info("Time: %s",pd.to_datetime(data['updateTime'], unit='ms'))
                                logging.info("Order ID: %s",data['orderId'])
                                logging.info("-----------------------------------------")

                            elif double_soldiers == "sell":

                                side = "SELL"
                                type = "MARKET"

                                data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
                                                    .format(symbol,side,type,quantity,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
                                                    .format(symbol,side,type,quantity,recvWindow,timestamp()), api_secret)), headers=headers).json()


                                # logging.info(data)

                                get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers).json()

                                logging.info("-----------------------------------------")
                                logging.info("Short position opened")
                                logging.info("Symbol: %s",data['symbol'])
                                logging.info("Type: %s",data['type'])
                                logging.info("Price:%s", get_positions[0]['entryPrice'])
                                logging.info("Volume:%s",data['origQty'])
                                logging.info("Time: %s",pd.to_datetime(data['updateTime'], unit='ms'))
                                logging.info("Order ID: %s",data['orderId'])
                                logging.info("-----------------------------------------")


                        #If is Long Position opened
                        elif float(i['positionAmt']) > 0:
                            position.LongOpened = True
                            position.ShortOpened = False

                            double_soldiers = Setups.Double_Soldiers_Strategy("{}".format(symbol),"1h").get_signal(api_key_md,api_secret_md)

                            if double_soldiers == "sell":

                                recvWindow = 1000000
                                side = "SELL"
                                type = "MARKET"

                                data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
                                                    .format(symbol,side,type,quantity * 2,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
                                                    .format(symbol,side,type,quantity * 2,recvWindow,timestamp()), api_secret)), headers=headers).json()

                                # logging.info(data)

                                get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers).json()

                                logging.info("-----------------------------------------")
                                logging.info("Short position opened")
                                logging.info("Symbol: %s",data['symbol'])
                                logging.info("Type: %s",data['type'])
                                logging.info("Price:%s", get_positions[0]['entryPrice'])
                                logging.info("Volume:%s",data['origQty'])
                                logging.info("Time: %s",pd.to_datetime(data['updateTime'], unit='ms'))
                                logging.info("Order ID: %s",data['orderId'])
                                logging.info("-----------------------------------------")


                        #If is Short Position opened
                        elif float(i['positionAmt']) < 0:
                            position.ShortOpened = True
                            position.LongOpened = False

                            double_soldiers = Setups.Double_Soldiers_Strategy("{}".format(symbol),"1h").get_signal(api_key_md,api_secret_md)

                            if double_soldiers == "buy":

                                recvWindow = 1000000
                                side = "BUY"
                                type = "MARKET"

                                data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
                                                    .format(symbol,side,type,quantity * 2,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
                                                    .format(symbol,side,type,quantity * 2,recvWindow,timestamp()), api_secret)), headers=headers).json()
                                # logging.info(data)

                                get_positions = requests.get(url+"?symbol={}&recvWindow={}&timestamp={}&signature={}".format(symbol,recvWindow,timestamp(),hashing("symbol={}&recvWindow={}&timestamp={}".format(symbol,recvWindow,timestamp()), api_secret)), headers=headers).json()

                                logging.info("-----------------------------------------")
                                logging.info("Long position opened")
                                logging.info("Symbol: %s",data['symbol'])
                                logging.info("Type: %s",data['type'])
                                logging.info("Price:%s", get_positions[0]['entryPrice'])
                                logging.info("Volume:%s",data['origQty'])
                                logging.info("Time: %s",pd.to_datetime(data['updateTime'], unit='ms'))
                                logging.info("Order ID: %s",data['orderId'])
                                logging.info("-----------------------------------------")

            except Exception as e:
                print(e)
                pass


    #If something happens, close all the orders.
    except Exception as e:
        
        print("Erro: {}".format(e))


        # if position.LongOpened == True:
        #     logging.info("The robot have Long Position opened, close it!")

        #     side = "SELL"
        #     type = "MARKET"

        #     data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
        #                         .format(symbol,side,type,quantity,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
        #                         .format(symbol,side,type,quantity,recvWindow,timestamp()), api_secret)), headers=headers).json()
        #     logging.info(data)
        #     logging.info("The position was closed")
        #     quit_gracefully()

        # elif position.ShortOpened == True:
        #     logging.info("The robot have Short Position opened, close it!")

        #     side = "BUY"
        #     type = "MARKET"

        #     data = requests.post(url_post+"?symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}&signature={}"
        #                         .format(symbol,side,type,quantity,recvWindow,timestamp(),hashing("symbol={}&side={}&type={}&quantity={}&recvWindow={}&timestamp={}"
        #                         .format(symbol,side,type,quantity,recvWindow,timestamp()), api_secret)), headers=headers)
        #     logging.info(data)
        #     logging.info("The position was closed")
        #     quit_gracefully()

        # else:
        #     quit_gracefully()
