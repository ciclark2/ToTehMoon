import datetime
import unirest
import hashlib
import random
import hmac
import string
import time
import json
import requests
import json
import urlparse
import itertools


class APIError(Exception):
	pass


class AuthenticationError(APIError):
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
	_KEY = 'cb90cbafd3131b11e2d2fe50da918897'
	_SECRET = '60169e196ef10057a817ca771b054cb0'
	_BASE_URL = 'http://demo-api.hitbtc.com'

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
		'nonce',
		'apikey',
		'clientOrderId',
		'symbol',
		'side',
		'price',
		'quantity',
		'type',
		'timeInForce',
	]
	_BALANCE = '/api/1/trading/balance'
	_BALANCE_PARAMS = []

	_ACTIVE_ORDERS = '/api/1/trading/orders/active?'
	_ACTIVE_ORDERS_PARAMS = [
		'symbols',
		'clientOrderId',
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
		url = self._BASE_URL + endpoint + query

		print url

		idx = query.find('clientOrderId')
		if idx == -1:
			raise APIError('something bad happened')
		else:
			params = query[idx:]

		print params
	
		signature = hmac.new(self._secret, endpoint + query, hashlib.sha512).hexdigest()

		idx2 = url.find('clientOrderId')
		if idx2 == -1: raise ValueError('poop!')

		url = url[:idx2 - 1]

		print 'url', url
		print 'sig', signature
		print 'params', params
		result = unirest.post(url, headers={"Api-Signature": signature}, params=params)

		return result

	@staticmethod
	def construct_nonce():
		"""
		Generate a pseudo-random nonce.

		:returns str:
		"""
		return str(int(time.mktime(datetime.datetime.now().timetuple()) * 1000 + datetime.datetime.now().microsecond / 1000))

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
		if not self._key and self._secret:
			raise AuthenticationError('A valid provisioned API key and secret are required to send orders')

		nonce = HitBTC.construct_nonce()
		clorid = ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(30))
		path = "/api/1/trading/new_order?apikey=" + self._key + "&nonce=" + nonce
		new_order = "clientOrderId=" + clorid + "&symbol=%s&side=%s&price=%s&quantity=%s&type=%s&timeInForce=%s" % (symbol, side, price, quantity, order_type, tif)

		signature = hmac.new(self._secret, path + new_order, hashlib.sha512).hexdigest()

		result = unirest.post("http://demo-api.hitbtc.com" + path, headers={"Api-Signature": signature}, params=new_order)
		
		return result

	def get_trading_balance(self):
		"""
		Get your current cash and reserved ccy balances.

		:returns dict:
		"""
		return self._request(self._BALANCE)

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
	
	#print 'Current exchange timestamp:'
	#print api.get_exchange_ts()
	#
	#print 'Live symbols:'
	#print api.get_symbols()
	#
	#print 'Live tickers:'
	#print api.get_tickers()

	#print 'BTCUSD Order Book:'
	#print api.get_order_book('BTCUSD')  

	print 'Send limit order:'
	print api.send_new_order('BTCUSD', 'buy', 425.0, 0.1).body

if __name__ == '__main__':
	main()
