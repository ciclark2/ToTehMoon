import requests
import json
import urlparse


class HitBTC(object):
	"""
	REST API for Hit BTC.
	"""
	_SECRET = '8fd089ce3e2642c1306624fce68c9f25Secretda0921b8de670901faeb39cb38f619d0l'
	_BASE_URL = 'http://api.hitbtc.com'

	_TIMESTAMP = '/api/1/public/time'
	_SYMBOLS = '/api/1/public/symbols'
	_SINGLE_TICKER = '/api/1/public/{symbol}/ticker'
	_ALL_TICKERS = '/api/1/public/ticker'
	_ORDER_BOOK = '/api/1/public/{symbol}/orderbook'
	_TRADES = '/api/1/public/{symbol}/trades'
	_RECENT_TRADES = '/api/1/public/{symbol}/trades/recent'

	def __init__(self, secret=_SECRET):
		"""
		API C'tor.
		
		:param str secret:
		"""
		self._secret = secret
		
		
	def _request(self, url):
		"""
		Send a GET request to the exchange.
		
		:param str url:
		"""
		url = urlparse.urljoin(self._BASE_URL, url)
		request = requests.get(url)
		if request.status_code != requests.codes.ok:
			raise IOError('URL failed "%s"' % url)

		return json.JSONDecoder().decode(request.text)

	def get_exchange_ts(self):
		return self._request(self._TIMESTAMP)

	def get_symbols(self):
		return self._request(self._SYMBOLS)

	def get_ticker(self, symbol):
		return self._request(self._SINGLE_TICKER.format(symbol=symbol))

	def get_tickers(self):
		return self._request(self._ALL_TICKERS)

	def get_order_book(self, symbol):
		return self._request(self._ORDER_BOOK.format(symbol=symbol))

	def get_trades(self, symbol):
		return self._request(self._TRADES.format(symbol=symbol))

	def get_recent_trades(self, symbol):
		return self._request(self._RECENT_TRADES.format(symbol=symbol))


def main():
	api = HitBTC()
	print api.get_exchange_ts()
	print api.get_symbols()
	print api.get_tickers()


if __name__ == '__main__':
	main()
