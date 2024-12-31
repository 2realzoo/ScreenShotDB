import os

# 루트 디렉토리
ROOT_DIR = os.path.dirname('./app.py')


# Data 디렉토리
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# ./data/image
IMAGE_DIR = os.path.join(DATA_DIR, 'image')
# ./data/image/raw
RAW_IMAGE_DIR = os.path.join(IMAGE_DIR, 'raw')
# ./data/image/organized
ORGANIZED_IMAGE_DIR = os.path.join(IMAGE_DIR, 'organized')


# DB 대용 파일
# ./data/storage
STORAGE_DIR = os.path.join(DATA_DIR, 'storage')

# ./data/storage/tags.json
TAG_FILE_PATH = os.path.join(STORAGE_DIR, 'tags.json')
# ./data/storage/storage.csv
STORAGE_FILE_PATH = os.path.join(STORAGE_DIR, 'storage.csv')


# 로그 파일 저장 경로 설정
# ./logs
LOG_DIR = os.path.join(ROOT_DIR, 'logs')


# 디렉토리 생성
os.makedirs(DATA_DIR, mode=0o777, exist_ok=True)
os.makedirs(IMAGE_DIR, mode=0o777, exist_ok=True)
os.makedirs(RAW_IMAGE_DIR, mode=0o777, exist_ok=True)
os.makedirs(ORGANIZED_IMAGE_DIR, mode=0o777, exist_ok=True)
os.makedirs(STORAGE_DIR, mode=0o777, exist_ok=True)
os.makedirs(LOG_DIR, mode=0o777, exist_ok=True)