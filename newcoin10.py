from utils.FileHandler import FileHandler
from apis.APIClient import APIClient
from apis.DataProcess import DataProcess
import os
from pathlib import Path
from dotenv import load_dotenv
env_path = os.path.join(Path("."), ".env")

def save_ohlcv_historical(df_list, option='s'):
    for l in df_list:
        id, df = l[0], l[1]
        if option == 's':
            file_handler.save_file(df=df, file_name=id)
        elif option == 'a':
            file_handler.update_file(df=df, file_name=id)
        else:
            return None
        
def update_id_list():
    listing_new_json = client.get_listing_new(limit=200)
    id_list = data_processor.process_listing_new(listing_new_json)
    return id_list

if __name__ == '__main__':
    # 讀取.env
    load_dotenv(env_path)

    # 初始化相關類別
    print('===== Initializing Parameters ==============')
    dir_path = '/ethereum_newcoin'
    file_handler = FileHandler(dir_path=dir_path)
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = os.getenv("X-CMC_PRO_API_KEY")
    client = APIClient(base_url=base_url, api_key=api_key)
    data_processor = DataProcess()
    # 獲取 ID 地圖，並生成字典
    print('===== Get ID Map ===========================')
    id_map_json = client.get_id_map(limit=5000)
    id_dict = data_processor.process_id_map(id_map_json)
    # 獲取最新上架幣種，並且篩選出24小時交易量前十名的幣種
    print('===== Retrieving id List ===================')
    id_list = update_id_list()
    id_string = ','.join(map(str, id_list))
    # 獲取這些前十名幣種的歷史數據(一個月)
    print('===== Retrieving OHLCV Historical Data =====')
    ohlcv_json = client.get_ohlcv_historical(id=id_string, count=720)
    print('===== Processing OHLCV Historical Data =====')
    df_list = data_processor.process_ohlcv_historical(json_result=ohlcv_json, id_dict=id_dict)
    # 歷史數據儲存到CSV檔案
    print('===== Saving the OHLCV Historical Data =====')
    save_ohlcv_historical(df_list)