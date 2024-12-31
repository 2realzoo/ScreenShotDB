import os
import json
from paddleocr import PaddleOCR

# 한국어와 영어 OCR 모델 초기화
ocr_korean = PaddleOCR(lang='korean')
ocr_english = PaddleOCR(lang='en')

def run_ocr(image_path):
    try:
        # 한국어 OCR 실행
        korean_result = ocr_korean.ocr(image_path, cls=False)
        
        # 영어 OCR 실행
        english_result = ocr_english.ocr(image_path, cls=False)
        
        # 결과 병합
        combined_result = korean_result + english_result
        
        # 텍스트만 추출
        text_lines = [
            line[1][0]  # OCR 결과에서 텍스트만 추출
            for result in combined_result if result  # 결과가 None이 아닌 경우만 처리
            for line in result
        ]
        
        return text_lines if text_lines else []  # 텍스트가 없으면 빈 리스트 반환
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return []  # 예외 발생 시 빈 리스트 반환

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def process_folder(folder_path):
    # 모든 이미지의 텍스트를 저장할 리스트
    all_texts = []
    
    # 서브 폴더별 OCR 결과를 저장할 딕셔너리
    folder_results = {}

    # 이미지 확장자 설정
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

    # 폴더 내 모든 서브 폴더 탐색
    for root, dirs, files in os.walk(folder_path):
        # 서브 폴더별 OCR 결과 저장
        folder_name = os.path.basename(root)
        folder_ocr_file = os.path.join(root, f"{folder_name}_ocr_results.json")

        # 이미 OCR 결과 파일이 있으면 폴더 건너뛰기
        if os.path.exists(folder_ocr_file):
            print(f"Skipping folder {folder_name} as OCR results already exist.")
            continue

        folder_texts = []

        for filename in files:
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(root, filename)
                print(f"Processing image: {image_path}")
                
                # OCR 실행
                ocr_result = run_ocr(image_path)
                
                # OCR 결과가 없으면 건너뛰기
                if not ocr_result:
                    print(f"No text detected in {filename}")
                    continue

                folder_texts.extend(ocr_result)
                all_texts.extend(ocr_result)

        if folder_texts:
            # 서브 폴더별 결과 저장
            folder_results[folder_name] = folder_texts
            save_json(folder_texts, folder_ocr_file)
    
    # 전체 폴더의 OCR 결과 저장
    if all_texts:
        save_json(all_texts, os.path.join(folder_path, "all_ocr_results.json"))
    print("OCR results saved successfully.")

# 이미지가 있는 최상위 폴더 경로 설정
folder_path = 'C:/ScreenShotDB/Image_data'

# 폴더 내부의 모든 이미지에 대해 OCR 수행
process_folder(folder_path)


