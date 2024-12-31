import re
import string

def remove_special_characters(text):
    # URL 패턴을 감지하여 보호
    url_pattern = r'(https?://\S+|www\.\S+)'
    urls = re.findall(url_pattern, text)
    
    # URL을 임시 토큰으로 대체
    for i, url in enumerate(urls):
        text = text.replace(url, f'__URL_{i}__')
    
    # 특수 문자를 제거 (알파벳, 숫자, 공백, .,!? 만 남김)
    text = re.sub(r'[^a-zA-Z0-9가-힣\s.,!?]', '', text).strip()
    text = re.sub(r'\b[A-Za-z]*\d+[A-Za-z]*\b', '', text).strip()

    # URL 토큰을 원래 URL로 복원
    for i, url in enumerate(urls):
        text = text.replace(f'__URL_{i}__', url)
    
    return text

    
def clean_text(text):
    pattern = f"[{re.escape(string.punctuation)}]"
    cleaned_text = re.sub(pattern, '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


