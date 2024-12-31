from pathlib import Path
import gradio as gr
import os
from PIL import Image
from models.ocr_models import OCRModel
from utils.preprocessing_img import remove_status_bar
from utils.handle_text import remove_special_characters
from utils.handle_data import save_image, save_image_2, make_dataframe
from services.summary import make_summary
from services.tag import tag_document, load_tags
from services.search import search_with_just_keyword, search_document
from dependencies.model_factory import ocr_model, gpt_chat_model
import logging
from config.path import RAW_IMAGE_DIR
import ast


# 예제 요약 및 태그 데이터
Chatbot = "OOO하는 방식도 추천드립니다."

previous_results = []

def get_text(img):
    ocr_text = ocr_model.get_text_from_image(img)
    removed_special_chars = remove_special_characters(ocr_text)
    return gpt_chat_model.strip_noise_from_text(removed_special_chars)

def display_images_and_summary(image_path):
    # try:
        img = Image.open(image_path)
        file_uuid = image_path.split('\\')[-2]
        if (search_result:=search_with_just_keyword(file_uuid)):
            summary = search_result[0]['summary']
            tags = ast.literal_eval(search_result[0]['tags'])
            if isinstance(tags, list) and len(tags) > 1:
                categories = ", ".join(tags)
            else:
                categories = tags
            chatbot_message = Chatbot
        else:
            # 스테이터스바 제거
            processed_image = remove_status_bar(img) 
            # ocr
            ocr_text = get_text(processed_image)
            summary = make_summary(ocr_text)
            
            tag = tag_document(ocr_text) # TODO: 현재 기존에 있는 tag인 경우 하나 밖에 안 나오게 되어 있는 것으로 확인함
            if isinstance(tag, list) and len(tag) > 1:
                categories = ", ".join(tag)
            else:
                categories = tag
            
            uuid_str, file_path = save_image_2(image_path)
            document_data = {'uuid_str':uuid_str, 'text':ocr_text, 'file_path': file_path, 'tags':categories, 'summary' : summary}
            make_dataframe(document_data)
            save_image_2(image_path)

        chatbot_message = Chatbot
        return img, summary, categories, chatbot_message
    # except Exception as e:
    #     logging.error(f"이미지 처리 중 오류 발생: {str(e)}")
    # return None, f"이미지를 처리할 수 없습니다.", "", ""

# def search_images_by_category(search_query):
#     base_dir = './organized_images'
#     matched_images = []
#     seen_filenames = set()
    
#     search_query = search_query.lower()
#     for category in example_categories:
#         if search_query in category.lower():
#             for category_folder in os.listdir(base_dir):
#                 category_folder_path = os.path.join(base_dir, category_folder)
#                 if os.path.isdir(category_folder_path):
#                     for img_file in os.listdir(category_folder_path):
#                         if img_file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
#                             if img_file not in seen_filenames:
#                                 img_path = os.path.join(category_folder_path, img_file)
#                                 matched_images.append(img_path)
#                                 seen_filenames.add(img_file)
    
#     return matched_images if matched_images else []

def fetch_images_from_folder(tag_name):
    results = [search_result['file_path'] for search_result in search_with_just_keyword(tag_name)]
    return results


def fetch_representative_images():
    folders = [tag for tag in load_tags().keys()]
    return folders


# update_selected_image 함수 추가
def update_selected_image(tag_name):
    images = fetch_images_from_folder(tag_name)
    return images

def update_image_and_summary(evt: gr.SelectData):
    selected_image_data = evt.value

    if isinstance(selected_image_data, dict) and "image" in selected_image_data:
        selected_image_path = selected_image_data["image"].get("path")

        if selected_image_path and os.path.exists(selected_image_path):
            img, summary, categories, chatbot_message = display_images_and_summary(selected_image_path)
            return img, summary, categories, chatbot_message

    return None, "이미지를 찾을 수 없습니다.", "", ""

with gr.Blocks() as app:
    with gr.Column():
        gr.Markdown("### 이미지 검색/요약")

        with gr.Row():
            folder_list = gr.Radio(choices=fetch_representative_images(), label="태그별 폴더 목록")
            infolder_images = gr.Gallery(label="이미지 목록", elem_id="infolder_image", columns=10, rows=2, height="100px", value=None, allow_preview=False, interactive=False)
        
        with gr.Row():
            search_input = gr.Textbox(label="검색", placeholder="검색할 키워드 및 내용을 입력하세요", scale=8)
            search_button = gr.Button("검색", scale=2)
        
        gallery_info = gr.Markdown(value="")

        def handle_search(search_query):
            global previous_results
            results = [search_result['file_path'] for search_result in search_with_just_keyword(search_query)]
            if results == previous_results:
                return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
            
            previous_results = results
            if results:
                return results, "▶검색된 이미지 표시", None, "", "", ""
            else:
                return [], "▶검색 결과가 없습니다. 다른 키워드로 검색해주세요.", None, "이미지를 찾을 수 없습니다.", "검색된 결과가 없습니다", ""
        
        search_results = gr.Gallery(label="검색 결과 이미지", elem_id="gallery", columns=5, height="200px", allow_preview=False, interactive=False)
             
    with gr.Row():
        with gr.Column(scale=1):
            selected_image_display = gr.Image(label="이미지", width=480, height=650)
        with gr.Column(scale=2):
            tags_display = gr.Textbox(label="태그", interactive=False)
            selected_summary_display = gr.Textbox(label="요약", interactive=False, lines=10)
            chatbot_display = gr.Textbox(label="Chatbot", interactive=False, lines=10)

    folder_list.change(
        fn=update_selected_image,
        inputs=folder_list,
        outputs=infolder_images
    )

    def display_selected_infolder_image(evt: gr.SelectData, images):
        selected_image_path = evt.value["image"]["path"]
        if selected_image_path and os.path.exists(selected_image_path):
            img, summary, categories, chatbot_message = display_images_and_summary(selected_image_path)
            return img, summary, categories, chatbot_message
        return None, "이미지를 찾을 수 없습니다.", "", ""

    infolder_images.select(
        fn=display_selected_infolder_image,
        inputs=infolder_images,
        outputs=[selected_image_display, selected_summary_display, tags_display, chatbot_display]
    )
    
    search_button.click(fn=handle_search, inputs=search_input, outputs=[search_results, gallery_info, selected_image_display, selected_summary_display, tags_display, chatbot_display])
    search_results.select(fn=update_image_and_summary, outputs=[selected_image_display, selected_summary_display, tags_display, chatbot_display])

app.launch(share=True)
