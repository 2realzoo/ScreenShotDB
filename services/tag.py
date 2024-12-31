from sentence_transformers import util
from dependencies.model_factory import device, embedding_model, topic_classification_model
import torch
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
from config.path import TAG_FILE_PATH

tag_file = Path(TAG_FILE_PATH)

def load_tags():
    if tag_file.exists():
        with open(tag_file, 'r') as file:
            return json.load(file)
    return defaultdict(dict)

tags = load_tags()

def save_tags(tags):
    with open(TAG_FILE_PATH, 'w') as f:
        json.dump(tags, f, indent=4)
        
def tag_document(text):
    # 새로운 태그 저장
    new_tags = []
    
    # 유사한 기존 태그 저장
    exist_tags = []
    similarity_threshold = 0.85  # 임계값
    
    classification = topic_classification_model.exec(text)
    splitted_tags = classification.split(',')
        
    for cur_tag in splitted_tags:
        cur_tag = cur_tag.strip()  # 공백 제거
        cur_tag_embedding = embedding_model.encode(cur_tag, device=device, convert_to_tensor=True)
        cur_simuilarity = False
        for tag_name, tag_info in tags.items():
            tag_embedding = torch.tensor(tag_info['embedding']).to(device)
            similarity = util.pytorch_cos_sim(cur_tag_embedding, tag_embedding).item()
            if similarity > similarity_threshold: 
                exist_tags.append(tag_name)
                cur_simuilarity = True
                # 여러 개 비슷한 경우도 전부 추가, 대신 임계값을 높임
        if not cur_simuilarity:       
            new_tags.append(cur_tag)
            tags[cur_tag] = {
                'embedding': cur_tag_embedding.tolist()
            }
    
    save_tags(tags)
            
    # print("Classification:", classification)
    result = new_tags + exist_tags
    return result
    
