import uuid
import requests

from config_live import buy_signal_settings, revenyou_api_url

def send_request(pair):
    revenyou_api_signal = create_revenyou_buy_signal(pair=pair)
    response = requests.post(url = revenyou_api_url.strip("\n"), json = revenyou_api_signal, headers = {'content-type': 'application/json'})

    print('response revenyou api on buy signal for pair {}: {}'.format(pair, response.json()))

def create_revenyou_buy_signal(pair):
    api_signal = {    
        'signalProvider': buy_signal_settings.get('signal_provider'),
        'signalProviderKey': buy_signal_settings.get('signal_provider_key'),
        'exchange': buy_signal_settings.get('exchange'),
        'symbol': pair.upper(),
        'signalType': 'buy',
        'signalId': str(uuid.uuid4()),
        'priceLimit': buy_signal_settings.get(pair).get('price_limit'),
        'buyTTLSec': buy_signal_settings.get(pair).get('buy_ttl_sec'),
        'takeProfit': [
            {
                'amountPercentage': '60',
                'pricePercentage': buy_signal_settings.get(pair).get('take_profit_price_percentage_60')
            },
            {
                'amountPercentage': '40',
                'pricePercentage': buy_signal_settings.get(pair).get('take_profit_price_percentage_40')
            }
        ],
        'stopLoss': {
            'pricePercentage': buy_signal_settings.get(pair).get('stop_loss_price_percentage')
        },
        'panicSell': {
            'pricePercentage': buy_signal_settings.get(pair).get('panic_sell_price_percentage'),
            'sellPriceDeviationPercentage': buy_signal_settings.get(pair).get('panic_sell_price_deviation_percentage')
        }
    }

    return api_signal