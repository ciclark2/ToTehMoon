import datetime
import unirest
import hashlib
import hmac
import time
import json
import requests
import json
import urlparse
import itertools


class APIError(Exception):
	pass


class InvalidAPIKey(APIError):
	pass


class NonceHasBeenUsed(APIError):
	pass


class NonceInvalid(APIError):
	pass


class WrongSignature(APIError):
	pass


class ExchangeError(APIError):
	pass


class HitBTC(object):
	"""
	REST API for Hit BTC.
	"""
	_KEY = None
	_SECRET = None
	_BASE_URL = 'http://api.hitbtc.com'

	# Market data URLS
	_TIMESTAMP = '/api/1/public/time'
	_SYMBOLS = '/api/1/public/symbols'
	_SINGLE_TICKER = '/api/1/public/{symbol}/ticker'
	_ALL_TICKERS = '/api/1/public/ticker'
	_ORDER_BOOK = '/api/1/public/{symbol}/orderbook'
	_TRADES = '/api/1/public/{symbol}/trades'
	_RECENT_TRADES = '/api/1/public/{symbol}/trades/recent'

	# Trading URLS
	_NEW_ORDER = '/api/1/trading/new_order?'
	_NEW_ORDER_PARAMS = [
		'apikey',
		'nonce',
		'clientOrderId',
		'symbol',
		'side',
		'price',
		'quantity',
		'type',
		'timeInForce',
	]

	def __init__(self, key=_KEY, secret=_SECRET):
		"""
		API C'tor.
	
		:param str key: API key	
		:param str secret: Secret key
		"""
		self._key = key
		self._secret = secret
		self._client_order_id = itertools.count(0)		
		
	def _request(self, url):
		"""
		Send a GET request to the exchange.
		
		:param str url:
		:raises APIError on unsuccessful request:
		"""
		url = urlparse.urljoin(self._BASE_URL, url)
		request = requests.get(url)
		if request.status_code != requests.codes.ok:
			raise APIError('Request to URL "{0}" failed'.format(url))

		return json.JSONDecoder().decode(request.text)

	def _post(self, endpoint, query):
		"""
		Send a POST to the exchange.

		:param str endpoint:
		:param str query:
		:returns result:
		"""
		nonce = str(int(time.mktime(datetime.datetime.now().timetuple()) * 1000 + datetime.datetime.now().microsecond / 1000))
		client_order_id = self._client_order_id.next()
		url = urlparse.urljoin(self._BASE_URL, endpoint, query)
		
		signature = hmac.new(self._secret, endpoint + query, hashlib.sha512).hexdigest()

		result = unirest.post(url, headers={"Api-Signature": signature}, params=query)

		return result

	@staticmethod
	def construct_query_string(fields, values):
		"""
		Construct a REST query string from a set of fields and values.

		:param list of str fields:
		:param list of str values:
		:returns str:
		"""
		field_values = zip(fields, values)
		return '&'.join(['{0}={1}'.format(*field) for field in field_values])

	def send_new_order(self, symbol, side, price, quantity, order_type='limit', tif='IOC'):
		"""
		Send a new market limit order to the exchange.

		:param str symbol: BTCUSD
		:param str side: buy or sell
		:param float price: 
		:param int quantity:
		:param str order_type:
		:param str tif:
		:returns ExecutionReport:
		"""
		query = HitBTC.construct_query_string(self._NEW_ORDER_PARAMS, [symbol, side, price, quantity, order_type, tif])
		return self._post(self._NEW_ORDER, query)	

	def get_exchange_ts(self):
		"""
		Request the current exchange timestamp

		:returns int:
		"""
		response = self._request(self._TIMESTAMP)
		return response['timestamp']

	def get_symbols(self):
		"""
		Request the set of listed symbols.
		
		:returns list:
		"""
		request = self._request(self._SYMBOLS)
		return [symbol_info['symbol'] for symbol_info in request['symbols']] 


	def get_ticker(self, symbol):
		"""
		Request the ticker for a given symbol.

		:param str symbol:
		:returns dict:
		"""
		return self._request(self._SINGLE_TICKER.format(symbol=symbol))

	def get_tickers(self):
		"""
		Request all tickers.
		
		:returns dict:
		"""
		return self._request(self._ALL_TICKERS)

	def get_order_book(self, symbol):
		"""
		Request the order book for a given symbol.

		:param str symbol:
		:returns dict:
		"""
		return self._request(self._ORDER_BOOK.format(symbol=symbol))

	def get_order_books(self):
		"""
		Request the order books for all symbols.

		:returns dict:
		"""
		return dict((symbol, self.get_order_book(symbol)) for symbol in self.get_symbols())

	def get_trades(self, symbol):
		"""
		Request trade history for a symbol.

		:param str symbol:
		:returns dict:
		"""
		return self._request(self._TRADES.format(symbol=symbol))

	def get_recent_trades(self, symbol):
		"""
		Request the recent trades for a symbol.
		
		:param str symbol:
		:returns dict:
		"""
		return self._request(self._RECENT_TRADES.format(symbol=symbol))


def main():
	api = HitBTC()
	
	print 'Current exchange timestamp:'
	print api.get_exchange_ts()
	
	print 'Live symbols:'
	print api.get_symbols()
	
	print 'Live tickers:'
	print api.get_tickers()

	print 'BTCUSD Order Book:'
	print api.get_order_book('BTCUSD')  

	print 'Send limit order:'
	print api.send_new_order('BTCUSD', 'buy', 425.0, 0.1)

if __name__ == '__main__':
	main()
