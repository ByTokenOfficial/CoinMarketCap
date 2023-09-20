import json

def load_id_list(file_path):
    # 從文件讀取 JSON 格式的字串
    with open(file_path, 'r') as f:
        json_str = f.read()
    # 將 JSON 格式的字串轉換回 list
    id_list = json.loads(json_str)
    
    return id_list

def save_id_list(file_path, id_list):
    # 將 list 轉換為 JSON 格式的字串
    json_str = json.dumps(id_list)
    # 寫入文件
    with open(file_path, 'w') as f:
        f.write(json_str)