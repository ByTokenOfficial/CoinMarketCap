from apis.APIClient import APIClient
from apis.DataProcess import DataProcess
from utils.GoogleSheetHandler import GoogleSheetHandler
from utils.TimeConverter import convert_timezone
from utils.ScoreCalculator import *
from utils.GenerateDataframe import *
from utils.IDList import *
from utils.Load_Save_File import *
from dotenv import load_dotenv
import os

from datetime import datetime
import pytz

import logging

# 設定日誌文件的名稱和格式
log_file = 'output.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



if __name__ == '__main__':
    # 讀取.env
    load_dotenv()
    
    # 初始化參數
    major_rank = 20 # group1
    group2_rank = 50
    group3_rank = 100
    group4_rank = 150
    # minor_rank = 100
    # major_weight = 0.5
    # minor_weight = 1 - major_weight
    timezone = 'Asia/Taipei'
    category = '604f2753ebccdd50cd175fc1' # stablecoin
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = os.getenv("X-CMC_PRO_API_KEY")

    # Google Sheet 設置
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_path = '/Users/gsgitlt008/Documents/projects/CoinMarketCap/marketheat-aee8eaf21745.json'
    spreadsheet_id =  os.getenv("MAJORCOIN_SPREADSHEET_ID")
    major_sheet = 'major'
    group2_sheet = '21to50'
    group3_sheet = '51to100'
    group4_sheet = '101to150'
    move3place_sheet = 'move3place'
    move2place_sheet = 'move2place'
    move1place_sheet = 'move1place'
    new_entry = 'new_entry'

    # Major/Minor 資訊 JSON 檔名
    # major_info_list_path = 'major_info.json'
    # minor_info_list_path = 'minor_info.json'
    filter_id_list_path = 'filter_id_list.json'
    # 儲存每次的group1,2,3,4的排名
    major_rank_path = 'major_rank.json'
    group2_rank_path = 'group2_rank.json'
    group3_rank_path = 'group3_rank.json'
    group4_rank_path = 'group4_rank.json'

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
    worksheet_group2 = googlesheet_handler.spreadsheet.worksheet(group2_sheet)
    worksheet_group3 = googlesheet_handler.spreadsheet.worksheet(group3_sheet)
    worksheet_group4 = googlesheet_handler.spreadsheet.worksheet(group4_sheet)
    worksheet_move3place = googlesheet_handler.spreadsheet.worksheet(move3place_sheet)
    worksheet_move2place = googlesheet_handler.spreadsheet.worksheet(move2place_sheet)
    worksheet_move1place = googlesheet_handler.spreadsheet.worksheet(move1place_sheet)
    worksheet_new_entry = googlesheet_handler.spreadsheet.worksheet(new_entry)

    # 讀取worksheet標頭
    worksheet_major_header = worksheet_major.row_values(1)
    print("worksheet_major_header", worksheet_major_header)
    worksheet_group2_header = worksheet_group2.row_values(1)
    worksheet_group3_header = worksheet_group3.row_values(1)
    worksheet_group4_header = worksheet_group4.row_values(1)

    # 獲取所有代幣列表（1-150排名）
    id_map_json = client.get_id_map(limit=170) # 剛好返回150名
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
    group2_tokens = new_result[major_rank:group2_rank]
    print("\ngroup2_tokens", group2_tokens)
    group3_tokens = new_result[group2_rank:group3_rank]
    print("\ngroup3_tokens", group3_tokens)
    group4_tokens = new_result[group3_rank:group4_rank]
    print("\ngroup4_tokens", group4_tokens)
    move3place_list = []
    move2place_list = []
    move1place_list = []
    new_entry_list = []

    # 讀取ID列表
    # major_id_list = [token[0] for token in major_tokens]  # 取得ID
    # print("\nmajor_id_list", major_id_list)

    # 判斷是否為第一次執行，是否存在表頭
    worksheet_list = [worksheet_major, worksheet_group2, worksheet_group3, worksheet_group4]
    worksheet_header_list = [worksheet_major_header, worksheet_group2_header, worksheet_group3_header, worksheet_group4_header]
    # 寫入Columes
    major_header = ['1st', '2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th']
    group2_header = list(range(21,51))
    group3_header = list(range(51,101))
    group4_header = list(range(101,151))
    # 對應worksheet 的header list
    corresponding_header_list = [major_header, group2_header, group3_header, group4_header]
    token_col = ['UTC+8']
    for worksheet, worksheet_header, header in zip(worksheet_list, worksheet_header_list, corresponding_header_list):
        if not worksheet_header:
        # if not worksheet_major_header:
            # 產生標頭
            header = token_col + header
            print("\nheader", header)
            # 將 Dataframe 寫入 Google Sheet
            googlesheet_handler.append_row(worksheet=worksheet, _list=header)
            print("寫入google sheet表頭完成！")
    # else:
    # 獲取major tokens的slug，append 到major sheet
    major_slug_list = [token[3] for token in major_tokens] 
    print("\nmajor_slug_list", major_slug_list)
    group2_slug_list = [token[3] for token in group2_tokens]
    print("\ngroup2_slug_list", group2_slug_list)
    group3_slug_list = [token[3] for token in group3_tokens]
    print("\ngroup3_slug_list", group3_slug_list)
    group4_slug_list = [token[3] for token in group4_tokens]
    print("\ngroup4_slug_list", group4_slug_list)

    # 獲取現在時間UTC+8
    taipei_timezone = pytz.timezone("Asia/Taipei")
    taipei_time = datetime.now(taipei_timezone).strftime("%Y-%m-%d %H:%M:%S")
    print("\ntaipei_time", taipei_time)

    # 合併slug_list + taipei_time
    time_slug_list = [taipei_time] + major_slug_list
    print("\ntime_slug_list", time_slug_list)
    time_group2_slug_list = [taipei_time] + group2_slug_list
    time_group3_slug_list = [taipei_time] + group3_slug_list
    time_group4_slug_list = [taipei_time] + group4_slug_list

    # time_slug_list寫入googlesheet
    googlesheet_handler.append_row(worksheet=worksheet_major, _list=time_slug_list)
    googlesheet_handler.append_row(worksheet=worksheet_group2, _list=time_group2_slug_list)
    googlesheet_handler.append_row(worksheet=worksheet_group3, _list=time_group3_slug_list)
    googlesheet_handler.append_row(worksheet=worksheet_group4, _list=time_group4_slug_list)
    print("寫入google sheet排行完成！")

    # 判斷是否有前一次的group1,2,3,4的file，如果有任一沒有，就4個都存，然後跳出這次執行
    check_file_list = [major_rank_path, group2_rank_path, group3_rank_path, group4_rank_path]
    corresponding_slug_lists = [time_slug_list, time_group2_slug_list, time_group3_slug_list, time_group4_slug_list]
    if any(not os.path.isfile(path) for path in check_file_list):
        for path, slug_list in zip(check_file_list, corresponding_slug_lists):
            save_json_file(path, slug_list)
        print("第一次執行，存入group1,2,3,4的成員，跳出這次執行")
        exit()
    
    # 讀取上次的group1,2,3,4的成員
    previous_major_list = load_json_file(major_rank_path)
    previous_group2_list = load_json_file(group2_rank_path)
    previous_group3_list = load_json_file(group3_rank_path)
    previous_group4_list = load_json_file(group4_rank_path)

    # 對於每個group4的token，檢查上次在哪一組
    for token in group4_slug_list:
        # 如果前一次在group1
        # if token in previous_major_list:
        #     move3place_list.append(token)
        # # 如果前一次在group2
        # elif token in previous_group2_list:
        #     move2place_list.append(token)
        # # 如果前一次在group3
        # elif token in previous_group3_list:
        #     move1place_list.append(token)
        # 如果本來不在排行內，進到Group4當作新進入
        if token not in previous_major_list and token not in previous_group2_list and token not in previous_group3_list and token not in previous_group4_list:
            new_entry_list.append(token)

    # 對於每個group3的token，檢查上次在哪一組
    for token in group3_slug_list:
        # # 如果前一次在group1
        # if token in previous_major_list:
        #     move2place_list.append(token)
        # # 如果前一次在group2
        # elif token in previous_group2_list:
        #     move1place_list.append(token)
        # 如果本來不在排行內，進到Group3當作新進入
        if token not in previous_major_list and token not in previous_group2_list and token not in previous_group3_list and token not in previous_group4_list:
            new_entry_list.append(token)
        elif token in previous_group4_list:
            move1place_list.append(token)

    # 對於每個group2的token，檢查上次在哪一組
    for token in group2_slug_list:
        # # 如果前一次在group1
        # if token in previous_major_list:
        #     move1place_list.append(token)
        # 如果本來不在排行內，進到Group3當作新進入
        if token not in previous_major_list and token not in previous_group2_list and token not in previous_group3_list and token not in previous_group4_list:
            new_entry_list.append(token)
        elif token in previous_group4_list:
            move2place_list.append(token)
        elif token in previous_group3_list:
            move1place_list.append(token)

    # 對於每個group1的token，檢查上次在哪一組
    for token in major_slug_list:
        if token not in previous_major_list and token not in previous_group2_list and token not in previous_group3_list and token not in previous_group4_list:
            new_entry_list.append(token)
        elif token in previous_group4_list:
            move3place_list.append(token)
        elif token in previous_group3_list:
            move2place_list.append(token)
        elif token in previous_group2_list:
            move1place_list.append(token)


    # 讀取過去24小時數據，如果有新進入的，且在過去24小時內上榜超過12次，就append到new_star_list

    # 將move3place_list, move2place_list, move1place_list寫入googlesheet
    move3place_list = [taipei_time] + move3place_list
    move2place_list = [taipei_time] + move2place_list
    move1place_list = [taipei_time] + move1place_list

    googlesheet_handler.append_row(worksheet=worksheet_move3place, _list=move3place_list)
    googlesheet_handler.append_row(worksheet=worksheet_move2place, _list=move2place_list)
    googlesheet_handler.append_row(worksheet=worksheet_move1place, _list=move1place_list)
    print("前進組別判斷完成！")
    new_entry_list = [taipei_time] + new_entry_list
    googlesheet_handler.append_row(worksheet=worksheet_new_entry, _list=new_entry_list)
    print("新進組別判斷完成！")

    # 將group1,2,3,4的成員寫入json檔案
    save_json_file(major_rank_path, major_slug_list)
    save_json_file(group2_rank_path, group2_slug_list)
    save_json_file(group3_rank_path, group3_slug_list)
    save_json_file(group4_rank_path, group4_slug_list)
    print("覆寫group1,2,3,4的成員完成！")

# 將所有print改為logging.info
logging.info("worksheet_major_header %s", worksheet_major_header)
logging.info("result %s", result)
# logging.info("stablecoin_list %s", stablecoin_list)
logging.info("filter_list %s", filter_list)
logging.info("new_result %s", new_result)
logging.info("major_tokens %s", major_tokens)
logging.info("major_slug_list %s", major_slug_list)
logging.info("taipei_time %s", taipei_time)
logging.info("time_slug_list %s", time_slug_list)
