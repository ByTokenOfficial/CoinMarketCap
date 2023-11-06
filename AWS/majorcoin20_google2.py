import sys
sys.path.append('/home/ubuntu/projects/Majorcoin20/CoinMarketCap')
from apis.APIClient import APIClient
from apis.DataProcess import DataProcess
from utils.GoogleSheetHandler import GoogleSheetHandler
from utils.TimeConverter import convert_timezone
from utils.ScoreCalculator import *
from utils.GenerateDataframe import *
from utils.IDList import *
from dotenv import load_dotenv
import os

from datetime import datetime
import pytz


if __name__ == '__main__':
    os.chdir('/home/ubuntu/projects/Majorcoin20/CoinMarketCap')
    pwd = os.getcwd()
    print(pwd)
    # 讀取.env
    load_dotenv()
    
    # 初始化參數
    major_rank = 20
    # minor_rank = 100
    # major_weight = 0.5
    # minor_weight = 1 - major_weight
    timezone = 'Asia/Taipei'
    category = '604f2753ebccdd50cd175fc1' # stablecoin
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = os.getenv("X-CMC_PRO_API_KEY")

    # Google Sheet 設置
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_path = r'/home/ubuntu/projects/Majorcoin20/CoinMarketCap/marketheat-aee8eaf21745.json'
    spreadsheet_id =  os.getenv("MAJORCOIN_SPREADSHEET_ID")
    major_sheet = 'major'

    # Major/Minor 資訊 JSON 檔名
    major_info_list_path = 'major_info.json'
    # minor_info_list_path = 'minor_info.json'
    filter_id_list_path = 'filter_id_list.json'


    # 實例化
    client = APIClient(base_url=base_url, api_key=api_key)
    data_processor = DataProcess()
    googlesheet_handler = GoogleSheetHandler(
        scopes=scopes,
        cred_path=cred_path,
        spreadsheet_id=spreadsheet_id
    )
    # 獲取spreadsheet的worksheet
    worksheet_major = googlesheet_handler.spreadsheet.worksheet(major_sheet)

    # 讀取worksheet標頭
    worksheet_major_header = worksheet_major.row_values(1)
    print("worksheet_major_header", worksheet_major_header)

    # 獲取所有代幣列表（1-150排名）
    id_map_json = client.get_id_map(limit=157) # 剛好返回150名
    result = data_processor.process_ranking(json_result=id_map_json) # 需注意id_map_json會有重複結果
    print("result", result)

    # 獲取所有穩定幣列表(第一次執行才會獲取穩定幣列表，之後從filter_id_list.json讀取)
    if not os.path.isfile(filter_id_list_path):
        stablecoin_json = client.get_category_token(category_id=category)
        stablecoin_list = data_processor.process_category(json_result=stablecoin_json)
        print("\nstablecoin_list", stablecoin_list)
        WBTC_ID = [3717]
        filter_list = stablecoin_list + WBTC_ID
        print("\nfilter_list", filter_list)
        save_id_list(filter_id_list_path, filter_list)
    else:
        filter_list = load_id_list(filter_id_list_path)
        print("\nfilter_list", filter_list)

    # 過濾穩定幣=>排除穩定幣的lists
    new_result = data_processor.filter(l1=result, l2=filter_list)
    print("\nnew_result", new_result)


    # 分組為大小幣(有序)
    major_tokens = new_result[:major_rank]
    print("\nmajor_tokens", major_tokens)

    # 讀取ID列表
    # major_id_list = [token[0] for token in major_tokens]  # 取得ID
    # print("\nmajor_id_list", major_id_list)

    # 判斷是否為第一次執行
    if not worksheet_major_header:

        # 讀取Columes
        major_header = ['1st', '2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th']
        # major_symbol = [token[3] for token in major_tokens]  # 取得前X大symbol

        # 產生標頭
        token_col = ['UTC+8']
        major_header = token_col + major_header
        print("\nmajor_header", major_header)
        # 將 Dataframe 寫入 Google Sheet
        googlesheet_handler.append_row(worksheet=worksheet_major, _list=major_header)

    else:
        # 獲取major tokens的slug，append 到major sheet
        major_slug_list = [token[3] for token in major_tokens] 
        print("\nmajor_slug_list", major_slug_list)

        # 獲取現在時間UTC+8
        taipei_timezone = pytz.timezone("Asia/Taipei")
        taipei_time = datetime.now(taipei_timezone).strftime("%Y-%m-%d %H:%M:%S")
        print("\ntaipei_time", taipei_time)

        # 合併slug_list + taipei_time
        time_slug_list = [taipei_time] + major_slug_list
        print("\ntime_slug_list", time_slug_list)

        # time_slug_list寫入googlesheet
        googlesheet_handler.append_row(worksheet=worksheet_major, _list=time_slug_list)
