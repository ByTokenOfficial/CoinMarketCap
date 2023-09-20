import pandas as pd


class DataProcess:
    def __init__(self):
        pass
    
    def check_input(self, json_result):
        if json_result['status']['error_code'] != 0:
            error_message = json_result['status']['error_message']
            return False
        else:
            return True
        
    def process_quote(self, json_result):
        if not self.check_input(json_result): return None

        data = json_result['data']

        for token_symbol, token_data in data.items():
            # 數據處理
            token_data = token_data[0]
            quote = token_data['quote']['USD']
            # 提取所需數據
            max_supply = token_data['max_supply']
            circulating_supply = token_data['circulating_supply']
            total_supply = token_data['total_supply']
            is_active = token_data['is_active']
            infinite_supply = token_data['infinite_supply']
            cmc_rank = token_data['cmc_rank']
            price = quote['price']
            volume_24h = quote['volume_24h']
            volume_change_24h = quote['volume_change_24h']
            percent_change_1h = quote['percent_change_1h']
            percent_change_24h = quote['percent_change_24h']
            market_cap = quote['market_cap']
            market_cap_dominance = quote['market_cap_dominance']
            fully_diluted_market_cap = quote['fully_diluted_market_cap']

    def process_listing_new(self, json_result, chain='ETH'):
        if not self.check_input(json_result): return None

        tmp = []

        for token in json_result['data']:
            platform = token['platform']
            if platform is None: continue

            token_platform = platform['symbol']

            if token_platform == chain:
                price_volumn_dict = token['quote']['USD']
                volume_24h = price_volumn_dict['volume_24h']
                token_id = token['id']
                #slug = token['slug']
                #symbol = token['symbol']
                tmp.append([token_id, volume_24h])

        # 排序取前十大
        sorted_tmp = sorted(tmp, key=lambda l: l[1], reverse=True)
        trend = sorted_tmp[:10]
        # print(trend)

        # [[id1], [id2], ...]
        return [t[0] for t in trend]

    def process_ohlcv_historical(self, json_result, id_dict):
        if not self.check_input(json_result): return None

        data = json_result['data']

        result = []
        # 考慮多幣種
        # 依照所需要的提取內容進行提取
        for _, token_data in data.items():
            tmp_list = []
            id = token_data['id']
            quotes = token_data['quotes']
            # 在slug_dict中匹配name所對應的slug
            if id_dict[id]:
                token_slug = id_dict[id][0] #slug
            else:
                print(f'Cannot find the token id in our id dictionary.')
                continue
            # 數據處理
            for q in quotes:
                quote_dict = q['quote']['USD']
                tmp_list.append(quote_dict)

            df = pd.DataFrame(tmp_list)
            df.set_index('timestamp', inplace=True)

            result.append([token_slug, df])

        return result
    
    def process_single_ohlcv_historical(self, json_result, id_dict):
        if not self.check_input(json_result): return None

        token_data = json_result['data']
        id = token_data['id']
        quotes = token_data['quotes']

        if id_dict[id]:
            token_slug = id_dict[id][0] #slug
        else:
            print(f'Cannot find the token id in our id dictionary.')
            return
        
        if quotes:
            tmp = []
            for q in quotes:
                quote_dict = q['quote']['USD']
                tmp.append(quote_dict)
            df = pd.DataFrame(tmp)
            df.set_index('timestamp', inplace=True)
            return [[token_slug, df]]
        else:
            print('No New Quote Now')
            return
    
    def process_ohlcv_lastest(self, json_result):
        if not self.check_input(json_result): return None

        token_data = json_result['data']
        tmp = []
        for _, token_info in token_data:
            quote = token_info['quote']['USD']
            tmp.append(
                {
                    'timestamp': quote['last_updated'],
                    'token_id': token_info['id'],
                    'close': quote['close']
                }
            )
        df = pd.DataFrame(tmp)
        df.set_index('timestamp', inplace=True)

        return df
    
    def process_id_map(self, json_result):
        if not self.check_input(json_result): return None

        data = json_result['data']
        result = dict()

        for token_info in data:
            dict_key = token_info['id']
            dict_val1 = token_info['slug']
            dict_val2 = token_info['name']
            dict_val3 = token_info['symbol']
            result[dict_key] = [dict_val1, dict_val2, dict_val3]
        
        return result
    
    def process_ranking(self, json_result):
        if not self.check_input(json_result): return None

        data = json_result['data']
        # 需注意json_result中會有重複數據
        result = []

        for token_info in data:
            tmp = [
                token_info['id'],
                token_info['slug'],
                token_info['name'],
                token_info['symbol']
            ]
            if tmp not in result:
                result.append(tmp)
        
        return result
    
    def process_category(self, json_result):
        if not self.check_input(json_result): return None

        coins = json_result['data']['coins']
        id_list = []
        for token in coins:
            id_list.append(token['id'])

        return id_list
    
    def process_previous_close(self, json_result):
        if not self.check_input(json_result): return None

        token_dict = json_result['data']
        result_dict = dict()
        t = None
        for v in token_dict.values():
            dict_key = v['id']
            quote = v['quotes'][0]['quote']['USD']
            dict_value = quote['close']
            result_dict[dict_key] = dict_value
            if t is None:
                t = quote['timestamp']

        return t, result_dict

    def process_yesterday_close(self, json_result):
        if not self.check_input(json_result): return None

        token_dict = json_result['data']
        result_dict = dict()
        t = None
        for v in token_dict.values():
            dict_key = v['id']
            quote = v['quotes'][0]['quote']['USD']
            dict_value = quote['close']
            result_dict[dict_key] = dict_value
            if t is None:
                t = quote['timestamp']

        return t, result_dict
    
    def process_lastest_close(self, json_result):
        if not self.check_input(json_result): return None

        token_dict = json_result['data']
        result_dict = dict()
        t = None

        for v in token_dict.values():
            dict_key = v['id']
            quote = v['quote']['USD']
            dict_value = quote['close']
            result_dict[dict_key] = dict_value
            if t is None:
                t = quote['last_updated']

        return t, result_dict

    def filter(self, l1, l2):
        return [token for token in l1 if token[0] not in l2]
    

if __name__ == '__main__':
    data_processor = DataProcess()