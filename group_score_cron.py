from apis.APIClient import APIClient
from apis.DataProcess import DataProcess
from utils.GoogleSheetHandler import GoogleSheetHandler
from utils.TimeConverter import convert_timezone
from utils.ScoreCalculator import *
from utils.GenerateDataframe import *
from utils.IDList import *
from dotenv import load_dotenv
import os


if __name__ == '__main__':
    # 讀取.env
    load_dotenv()
    
    # 初始化參數
    major_rank = 20
    minor_rank = 100
    major_weight = 0.5
    minor_weight = 1 - major_weight
    timezone = 'Asia/Taipei'
    category = '604f2753ebccdd50cd175fc1' # stablecoin
    base_url = 'https://pro-api.coinmarketcap.com/'
    api_key = os.getenv("X-CMC_PRO_API_KEY")

    # Google Sheet 設置
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_path = '/Users/gsgitlt008/Documents/projects/CoinMarketCap/marketheat-aee8eaf21745.json'
    spreadsheet_id =  os.getenv("SPREADSHEET_ID")
    major_sheet = 'major'
    minor_sheet = 'minor'
    total_score_sheet = 'total_score'
    stats_major_sheet = 'stats_major'
    stats_minor_sheet = 'stats_minor'

    # Major/Minor 資訊 JSON 檔名
    major_info_list_path = 'major_info.json'
    minor_info_list_path = 'minor_info.json'

    # 實例化
    client = APIClient(base_url=base_url, api_key=api_key)
    data_processor = DataProcess()
    googlesheet_handler = GoogleSheetHandler(
        scopes=scopes,
        cred_path=cred_path,
        spreadsheet_id=spreadsheet_id
    )
    worksheet_major = googlesheet_handler.spreadsheet.worksheet(major_sheet)
    worksheet_minor = googlesheet_handler.spreadsheet.worksheet(minor_sheet)
    worksheet_total_score = googlesheet_handler.spreadsheet.worksheet(total_score_sheet)
    worksheet_stats_major = googlesheet_handler.spreadsheet.worksheet(stats_major_sheet)
    worksheet_stats_minor = googlesheet_handler.spreadsheet.worksheet(stats_minor_sheet)

    # 讀取worksheet標頭
    worksheet_major_header = worksheet_major.row_values(1)
    worksheet_minor_header = worksheet_minor.row_values(1)
    worksheet_total_score_header = worksheet_total_score.row_values(1)
    worksheet_stats_major_header = worksheet_stats_major.row_values(1)
    worksheet_stats_minor_header = worksheet_stats_minor.row_values(1)

    # 判斷是否為第一次執行
    if not worksheet_major_header:
        # 獲取所有代幣列表（1-150排名）
        id_map_json = client.get_id_map(limit=157) # 剛好返回150名
        result = data_processor.process_ranking(json_result=id_map_json) # 需注意id_map_json會有重複結果

        # 獲取所有穩定幣列表
        stablecoin_json = client.get_category_token(category_id=category)
        stablecoin_list = data_processor.process_category(json_result=stablecoin_json)
        
        # 過濾穩定幣
        new_result = data_processor.filter(l1=result, l2=stablecoin_list)

        # 分組為大小幣(有序)
        major_tokens = new_result[:major_rank]
        minor_tokens = new_result[major_rank:minor_rank]
        
        # 讀取ID列表
        major_id_list = [token[0] for token in major_tokens]
        minor_id_list = [token[0] for token in minor_tokens]
        # 讀取Columes
        major_header = [token[3] for token in major_tokens]
        minor_header = [token[3] for token in minor_tokens]

        # 產生標頭 Dataframe
        token_col = ['Data']
        major_header = token_col + major_header
        print("\nmajor_header", major_header)
        minor_header = token_col + minor_header
        
        timestamp_header = ['Timestamp']
        total_score_header = [
                            'Raw Major Score',
                            'Major Weight',
                            'Major Score',
                            'Raw Minor Score',
                            'Minor Weight',
                            'Minor Score',
                            'Total Score'
                            ]
        total_score_header = timestamp_header + total_score_header
        
        score_header = [str(n) for n in range(-4, 5)]
        stats_major_header = stats_minor_header = timestamp_header + score_header
        # 將 Dataframe 寫入 Google Sheet
        googlesheet_handler.append_row(worksheet=worksheet_major, header=major_header)
        googlesheet_handler.append_row(worksheet=worksheet_minor, header=minor_header)
        googlesheet_handler.append_row(worksheet=worksheet_total_score, header=total_score_header)
        googlesheet_handler.append_row(worksheet=worksheet_stats_major, header=stats_major_header)
        googlesheet_handler.append_row(worksheet=worksheet_stats_minor, header=stats_minor_header)
        # 存儲ID列表為JSON檔案
        save_id_list(file_path=major_info_list_path, id_list=major_id_list)
        save_id_list(file_path=minor_info_list_path, id_list=minor_id_list)

    else:
        # 讀取JSON檔案(Major, Minor)
        major_id_list = load_id_list(file_path=major_info_list_path)
        minor_id_list = load_id_list(file_path=minor_info_list_path)

        # 發送Major+Minor請求
        all_id_list = major_id_list + minor_id_list
        all_ids = ','.join(map(str, all_id_list))

        # 獲取往前24小時的收盤價
        previous_all_result_json = client.get_ohlcv_historical(id=all_ids, count=25)
        previous_timestamp, previous_id_price_dict = data_processor.process_previous_close(json_result=previous_all_result_json)
        # UTC -> UTC+8
        previous_timestamp = convert_timezone(t=previous_timestamp, timezone=timezone)

        # 獲取最近一根K棒的收盤價
        lastest_all_result_json = client.update_ohlcv_lastest(id=all_ids)
        lastest_timestamp, lastest_id_price_dict = data_processor.process_lastest_close(json_result=lastest_all_result_json)
        lastest_timestamp = convert_timezone(t=lastest_timestamp, timezone=timezone)
        
        # 計算24小時漲跌百分比
        pct_change_dict = cal_pct_change(prev_price_dict=previous_id_price_dict,
                                        lastest_price_dict=lastest_id_price_dict)
        # print(pct_change_dict)
        
        # 計算分數
        score_dict = cal_score(pct_change_dict=pct_change_dict)

        # 分數字典
        major_score_dict = generate_score_dict(score_dict=score_dict, token_id_list=major_id_list)
        minor_score_dict = generate_score_dict(score_dict=score_dict, token_id_list=minor_id_list)

        # 計算大小幣總分
        major_total_score = cal_total_score(s_dict=major_score_dict)
        minor_total_score = cal_total_score(s_dict=minor_score_dict)

        # 產生DataFrame
        major_df = generate_df(
                                header=worksheet_major_header, id_list=major_id_list,
                                previous_timestamp=previous_timestamp, lastest_timestamp=lastest_timestamp,
                                previous_id_price_dict=previous_id_price_dict, lastest_id_price_dict=lastest_id_price_dict,
                                pct_change_dict=pct_change_dict, score_dict=score_dict
                                )
        minor_df = generate_df(
                                header=worksheet_minor_header, id_list=minor_id_list,
                                previous_timestamp=previous_timestamp, lastest_timestamp=lastest_timestamp,
                                previous_id_price_dict=previous_id_price_dict, lastest_id_price_dict=lastest_id_price_dict,
                                pct_change_dict=pct_change_dict, score_dict=score_dict
                                )
        total_score_df = generate_score_df(
                                            lastest_timestamp=lastest_timestamp,
                                            major_score=major_total_score,
                                            major_weight=major_weight,
                                            minor_score=minor_total_score,
                                            minor_weight=minor_weight
                                            )
        stats_major_df = generate_stats_df(
                                            header=worksheet_stats_major_header,
                                            stats_dict=major_score_dict,
                                            lastest_timestamp=lastest_timestamp
                                            )
        stats_minor_df = generate_stats_df(
                                            header=worksheet_stats_minor_header,
                                            stats_dict=minor_score_dict,
                                            lastest_timestamp=lastest_timestamp
                                            )

        # Google Sheet逐個row寫入
        googlesheet_handler.append_rows(worksheet=worksheet_major, df=major_df)
        googlesheet_handler.append_rows(worksheet=worksheet_minor, df=minor_df)
        googlesheet_handler.append_rows(worksheet=worksheet_total_score, df=total_score_df)
        googlesheet_handler.append_rows(worksheet=worksheet_stats_major, df=stats_major_df)
        googlesheet_handler.append_rows(worksheet=worksheet_stats_minor, df=stats_minor_df)