import requests

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key
        }

    def check_response(self, response):
         # 檢查請求是否成功
        if response.status_code == 200:
            # 若成功，則返回JSON數據
            return response.json()
        else:
            # 若失敗，返回錯誤訊息
            return response.text
        
    def get_latest_crypto_quotes(self, symbol):
        endpoint = 'v2/cryptocurrency/quotes/latest'

        params = {
            'symbol': symbol
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def get_id_map(self, limit, sort='cmc_rank', status='active'):
        endpoint = 'v1/cryptocurrency/map'

        params = {
            'limit': limit,
            'sort': sort,
            'listing_status': status
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def get_listing_new(self, limit=100):
        endpoint = 'v1/cryptocurrency/listings/new'

        params = {
            'limit': limit
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def get_ohlcv_historical(self, id, count, time_period='hourly', interval='hourly'):
        endpoint = 'v2/cryptocurrency/ohlcv/historical'

        params = {
            'id': id,
            'time_period': time_period,
            'count': count,
            'interval': interval
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def update_ohlcv_historical(self, id, time_start, time_end, time_period='hourly', interval='hourly'):
        endpoint = 'v2/cryptocurrency/ohlcv/historical'

        params = {
            'id': id,
            'time_period': time_period,
            'interval': interval,
            'time_start': time_start,
            'time_end':time_end
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def update_ohlcv_lastest(self, id):
        # The lastest data is updated every 10 minutes.
        endpoint = 'v2/cryptocurrency/ohlcv/latest'

        params = {
            'id': id
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)
    
    def get_categories(self):
        pass

    def get_category_token(self, category_id):
        endpoint = 'v1/cryptocurrency/category'

        params = {
            'id': category_id
        }

        response = requests.get(url=self.base_url+endpoint, headers=self.headers, params=params)

        return self.check_response(response)

    
if __name__ == '__main__':
    # 示例用法
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = 'YOUR_API_KEY'

    client = APIClient(base_url, api_key)

    # response = client.get_latest_crypto_quotes(symbol='BTC')
    # print(response)
    str_id = '1,1027'
    response = client.update_ohlcv_lastest(id=str_id)
    print(response)