from paddleocr import PaddleOCR
from PIL import Image
import re
import string
import json
from pathlib import Path
from utils.handle_text import clean_text


class OCRModel():
    def __init__(self, lang:str='korean'):
        self.model = PaddleOCR(lang=lang)


    def make_wordlist(self, img_path):
        result = self.model.ocr(img_path, cls=False)
        word_list = []
        for i in result[0]:
            word_list.append(clean_text(i[1][0]))
        return word_list


    def get_text_from_image(self, preprocessed_img):
        ocr_result = self.model.ocr(preprocessed_img, cls=False)[0]
        
        # 텍스트와 좌표를 추출하고 y 좌표로 정렬
        y_threshold = 10
        sorted_results = sorted([(item[1][0], item[0][0][0], item[0][0][1]) for item in ocr_result], key=lambda x: x[2])

        # y 좌표를 기준으로 그룹화 : 같은 줄
        groups = []
        current_group = [sorted_results[0]]

        for item in sorted_results[1:]:
            if abs(item[2] - current_group[-1][2]) <= y_threshold:
                current_group.append(item)
            else:
                groups.append(current_group)
                current_group = [item]

        groups.append(current_group)
        # 각 그룹 내에서 x 좌표로 정렬하고 텍스트 연결 (기호 제거 적용)
        result = []
        for group in groups:
            sorted_group = sorted(group, key=lambda x: x[1])
            line_data = [clean_text(item[0]) for item in sorted_group]
            result.append(' '.join(line_data))
    
        return ' '.join(result)
    
    def make_json(self, img_path):
        img_name = Path(img_path).name
        ocr_result = self.model.ocr(img_path, cls=False)[0]
        
        # 텍스트와 좌표를 추출하고 y 좌표로 정렬
        y_threshold = 10
        sorted_results = sorted([(item[1][0], item[0][0][0], item[0][0][1]) for item in ocr_result], key=lambda x: x[2])

        # y 좌표를 기준으로 그룹화 : 같은 줄
        groups = []
        current_group = [sorted_results[0]]

        for item in sorted_results[1:]:
            if abs(item[2] - current_group[-1][2]) <= y_threshold:
                current_group.append(item)
            else:
                groups.append(current_group)
                current_group = [item]

        groups.append(current_group)
        # 각 그룹 내에서 x 좌표로 정렬하고 텍스트 연결 (기호 제거 적용)
        result = []
        for group in groups:
            sorted_group = sorted(group, key=lambda x: x[1])
            line_data = [{'text': clean_text(item[0]), 'coordinates': item[1]} for item in sorted_group]
            result.append(line_data)

        # 결과를 JSON 파일로 저장
        output_data = {
            "lines": result
        }
        
        # json파일 저장
        with open(f'data/cordinate_json/{img_name}.json', 'w', encoding='utf-8') as f: 
            json.dump(output_data, f, ensure_ascii=False, indent=4)

    