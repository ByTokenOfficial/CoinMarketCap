# 基於 CoinMarketCap APIs 的 Tokens 打分模型
## 功能介紹
- 依照自定義的排名範圍，將幣種分為大幣(Major Token)和小幣(Minor Token)。
- 依照漲跌幅級距進行分數轉化。
- 將大小幣價格資料以及分數分布寫入 Google Sheet 試算表。
- 搭配 Linux 系統中的 crontab 排程進行使用。
## 使用說明
### 依賴包安裝
```pip install -r requirements.txt``` 或 ```pip3 install -r requirements.txt```
### Google Sheet 權限設定
- 取得googlesheetAPI金鑰/憑證參考[此篇教程](https://medium.com/%E8%BB%9F%E9%AB%94%E9%96%8B%E7%99%BC/%E6%8B%BF-google-%E6%86%91%E8%AD%89-api-e92d87cb42af)
- 取得GoogleSheet ID參考[此篇教程](https://www.learncodewithmike.com/2020/08/python-write-to-google-sheet.html)。
- 將金鑰下載並放置於專案根目錄下。
### 程式碼說明
#### **apis/APIClient.py**
- APIClient類別，輸入 base_url 和 api_key 來建立實例。
- CoinMarketCap APIs 方法，參考[官方文件](https://coinmarketcap.com/api/documentation/v1/)。
#### **apis/DataProcess.py**
- DataProcess類別，用於處理 CoinMarketCap APIs 回傳的 JSON 資料。
#### **utils/FileHandler.py**
- FileHandler類別，用於處理 CSV 檔案讀寫。
#### **utils/GenerateDataframe.py**
- 用於生成大小幣價格資料的 Dataframe，此 Dataframe 將用來寫入 Google Sheet。
#### **utils/GoogleSheetHandler.py**
- GoogleSheetHandler類別，用於處理 Google Sheet 試算表讀寫。
#### **utils/IDList.py**
- 用於讀寫大小幣 ID 的 JSON 檔案。
#### **utils/ScoreCalculator.py**
- 用於計算大小幣分數及分佈的函數。
#### **utils/TimeConverter.py**
- 用於將 UTC 時間轉換為指定時區時間的函數，此處用於將 CoinMarketCap APIs 回傳的時間轉換為台北時間（UTC +8）。
#### **group_score_cron.py**
- 主程式，設計為搭配 Linux 系統中的 crontab 排程進行使用。
- 第一次執行前，須先在GoogleSheet上，手動建立major, minor, total_score, stats_major, stats_minor等5個分頁。
- 第一次執行時，會將大小幣 ID 寫入 JSON 檔案，並將 Header 寫入 Google Sheet 試算表。
- 之後每次執行時，會讀取大小幣 ID 的 JSON 檔，並將大小幣價格資料以及分數分布寫入 Google Sheet 試算表。
### Linux 排程設定
- 編輯排程。 \
```crontab -e```
- 設定每10分鐘執行一次。 \
```10 * * * * [Python解釋器絕對路徑] [group_score_cron.py絕對路徑] >> [正常輸出log檔的絕對路徑] 2>> [錯誤輸出log檔的絕對路徑] &```