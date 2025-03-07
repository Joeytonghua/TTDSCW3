import os
import requests
FILES = {
    "data/news.db": "1y4pPAGgZ06p5W7RQkqMK8R-WOKqsSmex",  # 你的 news.db 文件 ID
    "data/inverted_index.json": "1N9W_IL9KCxGDhCD-Zflc1Jtq0apVKPEW"  # 你的 inverted_index.json 文件 ID
}

def download_file(file_path, file_id):
    """从 Google Drive 下载文件"""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    if not os.path.exists(file_path):
        print(f"📥 Downloading {file_path} from Google Drive...")
        response = requests.get(url, stream=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ {file_path} download complete!")
    else:
        print(f"✅ {file_path} already exists.")

# 下载所有文件
for path, file_id in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    download_file(path, file_id)
