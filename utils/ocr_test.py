from utils.handle_text import remove_special_characters, get_text_from_image
from preprocessing_img import remove_status_bar
import numpy as np
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI


load_dotenv()

#### 요런 느낌으로 사용합니다.
data = './utils/ocr_test_data1.jpg'
processed_image = remove_status_bar(data) # 1. 스테이터스바 제거
ocr_result = get_text_from_image(data, np.array(processed_image)) # 2. OCR + 좌표기반. output: 단순 문자열
removed_special_chars = remove_special_characters(ocr_result) #3. url 외 특수문자열 제외

# 제일 똑똑한 애는 gpt-4o-mini 였음 (2개중 1위)
gpt_chat_model = ChatOpenAI(model='gpt-4o-mini')
llm_response = gpt_chat_model.invoke(removed_special_chars + ' 이 내용에서, 의미가 없는 문자열을 제거한 뒤, 온전히 그 내용만 돌려줘')
print(llm_response.content) # 4. 문자열 정제 완료!




 