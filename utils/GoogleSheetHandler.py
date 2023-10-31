import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetHandler:
    def __init__(self, scopes, cred_path, spreadsheet_id) -> None:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scopes)
        client = gspread.authorize(credentials)
        self.spreadsheet = client.open_by_key(spreadsheet_id)
    
    def append_row(self, worksheet, _list):
        worksheet.append_row(_list)

    def append_rows(self, worksheet, df):
        for row in range(df.shape[0]):
            worksheet.append_row(df.iloc[row].tolist())

if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_path = 'CREDENTIAL_PATH'
    spreadsheet_id = 'SPREADSHEET_ID'
    major_sheet = 'major'
    minor_sheet = 'minor'
    googlesheet_handler = GoogleSheetHandler(
        scopes=scopes,
        cred_path=cred_path,
        spreadsheet_id=spreadsheet_id
    )
    worksheet_major = googlesheet_handler.spreadsheet.worksheet(major_sheet)
    worksheet_minor = googlesheet_handler.spreadsheet.worksheet(minor_sheet)
    # 存Symbol 
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })

    googlesheet_handler.append_rows(worksheet=worksheet_major, df=df)