# pip install openai gradio faiss-cpu sentence-transformers pytesseract pillow
import openai
import gradio as gr
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# OpenAI API 설정
openai.api_key = "your_openai_api_key_here"

# 임베딩 모델 설정 (SentenceTransformers 사용)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 벡터 데이터베이스 설정 (FAISS)
dimension = 384  # all-MiniLM-L6-v2의 임베딩 차원
index = faiss.IndexFlatL2(dimension)

# 이미지 메타데이터 저장소 (임베딩과 연결)
image_metadata = []

# GPT-4를 통해 질문 생성 함수
def generate_questions(extracted_text):
    prompt = f"""
    The following is a text extracted from an image: "{extracted_text}"
    Based on this text, generate 3 intelligent follow-up questions that someone might ask to learn more about this topic. The questions should be concise and relevant:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # gpt-3.5-turbo도 사용 가능
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # GPT로부터 생성된 질문들을 반환
        questions = response.choices[0].message["content"].strip().split("\n")
        questions = [q.strip() for q in questions if q.strip()]
        return questions[:3]  # 최대 3개의 질문 반환

    except Exception as e:
        return [f"Error: {str(e)}"]

# 이미지 처리 함수
def process_image(image):
    # 이미지에서 텍스트 추출
    extracted_text = pytesseract.image_to_string(image)
    
    # 텍스트를 임베딩으로 변환
    text_embedding = embedding_model.encode([extracted_text])
    
    # 벡터 DB에 임베딩 추가
    index.add(np.array(text_embedding))
    image_metadata.append({"text": extracted_text, "image": image})
    
    # GPT-4를 이용해 질문 생성
    questions = generate_questions(extracted_text)
    
    return extracted_text, questions

# 선택된 질문에 따른 이미지 검색
def search_images_based_on_question(question):
    # 질문을 임베딩으로 변환
    question_embedding = embedding_model.encode([question])
    
    # 벡터 DB에서 가장 유사한 이미지 검색
    _, indices = index.search(np.array(question_embedding), k=3)
    
    # 검색된 이미지 반환
    results = [image_metadata[i]["image"] for i in indices[0]]
    return results

# Gradio 인터페이스 설정
app = gr.Blocks()

with app:
    gr.Markdown("# 이미지 기반 스마트 질문 생성 및 검색 챗봇")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="이미지 업로드")
            text_output = gr.Textbox(label="추출된 텍스트")
            question_suggestions = gr.Dropdown(label="추천 질문들", choices=[], interactive=True)
            search_results = gr.Gallery(label="검색된 이미지들").style(grid=[1, 3], height="auto")
            
            def update_suggestions(image):
                extracted_text, suggestions = process_image(image)
                return extracted_text, gr.Dropdown.update(choices=suggestions)
            
            def perform_search(question):
                results = search_images_based_on_question(question)
                return results

            image_input.change(fn=update_suggestions, inputs=image_input, outputs=[text_output, question_suggestions])
            question_suggestions.change(fn=perform_search, inputs=question_suggestions, outputs=search_results)

app.launch()