import sys
sys.path.append('/home/ubuntu/projects/Majorcoin20/CoinMarketCap')
from utils.FileHandler import FileHandler
from apis.APIClient import APIClient
from apis.DataProcess import DataProcess
from utils.GoogleSheetHandler import GoogleSheetHandler
import os
from pathlib import Path
from dotenv import load_dotenv
env_path = os.path.join(Path("../."), ".env")
from datetime import datetime
import pytz
import json

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
    # dir_path = '/data/2023-10-16_17-52'
    taipei_timezone = pytz.timezone("Asia/Taipei")
    save_time = datetime.now(taipei_timezone)
    save_time_format = save_time.strftime("%Y-%m-%d_%H-%M")
    dir_path = f'/data/{save_time_format}'
    # dir_path = os.path.join(data_path, save_time_format)
    # os.makedirs(dir_path, exist_ok=True)

    file_handler = FileHandler(dir_path=dir_path)
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = os.getenv("X-CMC_PRO_API_KEY")
    print(api_key)
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
    if ohlcv_json:
        print("Got Json!!")
    with open("ohlcv.json", "w", encoding="utf-8") as file:
        json.dump(ohlcv_json, file, ensure_ascii=True, indent=4)
    print('===== Processing OHLCV Historical Data =====')
    df_list = data_processor.process_ohlcv_historical(json_result=ohlcv_json, id_dict=id_dict)
    ## 新增打印10大交易量幣種
    slug_list = [slug_data[0] for slug_data in df_list]
    print("ranking", slug_list)
    ## 10大幣種串到google sheet
    print('===== Pushing Data to Google Sheet =====')
    ### Google Sheet 設置
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_path = r'/home/ubuntu/projects/Majorcoin20/CoinMarketCap/marketheat-aee8eaf21745.json'
    spreadsheet_id =  os.getenv("NEWCOINSHEET_ID")
    hourly_rank_sheet = 'Hourly_Rank'
    ### 實例化
    client = APIClient(base_url=base_url, api_key=api_key)
    data_processor = DataProcess()
    googlesheet_handler = GoogleSheetHandler(
        scopes=scopes,
        cred_path=cred_path,
        spreadsheet_id=spreadsheet_id
    )
    worksheet_hourly_rank = googlesheet_handler.spreadsheet.worksheet(hourly_rank_sheet)
    worksheet_hourly_rank_header = worksheet_hourly_rank.row_values(1)
    if not worksheet_hourly_rank_header:
        rank_header = ['UTC+8','1st', '2nd','3rd','4th','5th','6th','7th','8th','9th','10th']
        googlesheet_handler.append_row(worksheet=worksheet_hourly_rank, _list=rank_header)
    else:
        push_time_format = save_time.strftime("%Y-%m-%d_%H-%M-%S")
        ranking_list = [push_time_format] + slug_list
        googlesheet_handler.append_row(worksheet=worksheet_hourly_rank, _list=ranking_list)

    print('===== END Pushing Data =====')
    
    # 歷史數據儲存到CSV檔案
    # print('===== Saving the OHLCV Historical Data =====')
    # save_ohlcv_historical(df_list)

