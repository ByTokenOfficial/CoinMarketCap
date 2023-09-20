import os
import pandas as pd
import shutil

class FileHandler:
    def __init__(self, dir_path):
        self.dir_path = os.getcwd() + dir_path

    def save_file(self, df, file_name):
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        df.to_csv(f'{self.dir_path}/{file_name}.csv')

    def update_file(self, df, file_name):
        file_path = f'{self.dir_path}/{file_name}.csv'
        if not os.path.isfile(file_path):
            df.to_csv(file_path, index=True)
        else: # append
            df.to_csv(file_path, mode='a', header=False, index=True)

    def read_file(self, file_name):
        return pd.read_csv(f'{self.dir_path}/{file_name}.csv')
        
    def compress_folder(self, zip_filename):
        # 檢查文件夾是否存在
        if not os.path.exists(self.dir_path):
            return f"Error: The folder {self.dir_path} does not exist."

        # 壓縮文件夾
        shutil.make_archive(zip_filename, 'zip', self.dir_path)

        return f"Folder {self.dir_path} has been compressed to {zip_filename}.zip"
    
    def get_csv_filenames(self):
        csv_filenames = []
        for filename in os.listdir(self.dir_path):
            if filename.endswith('.csv'):
                csv_filenames.append(filename)
        return csv_filenames
    
    def extract_csv_filenames(self, csv_filenames):
        filenames = []
        for filename in csv_filenames:
            filenames.append(filename[:-4])
        return filenames

    def get_last_timestamp_from_csv(self, file):
        df = pd.read_csv(f'{self.dir_path}/{file}.csv')
        return df.iloc[-1].timestamp
    
    def get_last_volume_from_csv(self, file):
        df = pd.read_csv(f'{self.dir_path}/{file}.csv')
        return df.iloc[-1].volume
    
    def get_last_row_from_csv(self, file):
        df = pd.read_csv(f'{self.dir_path}/{file}.csv')
        return df.iloc[-1]
    
    def calculate_volume_change(self, file):
        df = pd.read_csv(f'{self.dir_path}/{file}.csv')
        # 若為第一個小時新出的
        if df.shape[0] == 1:
            return df.iloc[0].volume
        # 非第一個小時新出
        return df.iloc[-1].volume - df.iloc[-2].volume

if __name__ == '__main__':
    # 示例用法
    dir_path = 'DIR_PATH'
    data = {'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Tokyo']}
    df = pd.DataFrame(data)

    # 创建文件访问对象
    file_handler = FileHandler(dir_path)

    # 保存数据到文件
    file_handler.save_file(df=df, file_name='test')
