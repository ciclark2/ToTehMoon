import datetime
import hashlib
import hmac
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
	_NEW_ORDER = '/api/1/trading/new_order?apikey={key}&nonce={nonce}&clientOrderId={clorid}&symbol={symbol}&side={side}&price={price}&quantity={size}&type={type}'

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

	def _post(self, url):
		"""
		Send a POST to the exchange.

		:param str data:
		:returns result:
		"""
		nonce = str(int(time.mktime(datetime.datetime.now().timetuple()) * 1000 + datetime.datetime.now().microsecond / 1000))
		client_order_id = self._client_order_id.next()
		url = urlparse.urljoin(self._BASE_URL, url)
		
		signature = hmac.new(self._secret, url, hashlib.sha512).hexdigest()

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
	print api.get_exchange_ts()
	print api.get_symbols()
	print api.get_tickers()


if __name__ == '__main__':
	main()
