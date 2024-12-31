import faiss
import pandas as pd
from dependencies.model_factory import embedding_model
from config.path import STORAGE_FILE_PATH

def search_with_just_keyword(keyword):
    if not keyword:
        return []
    # 전체 로드
    df = pd.read_csv(STORAGE_FILE_PATH)

    # 1. 키워드로 필터링
    # text, summary, tags 컬럼에서 키워드가 포함된 문서를 필터링
    filtered_df = df[df['file_path'].str.contains(keyword, na=False) |
                    df['text'].str.contains(keyword, na=False) |
                    df['summary'].str.contains(keyword, na=False) |
                    df['tags'].str.contains(keyword, na=False)].copy()
    search_result = []
    # 필터링된 결과 출력
    if not filtered_df.empty:
        cur_row = {}
        for _, row in filtered_df.iterrows():
            cur_row['file_path'] = row['file_path']
            cur_row['text'] = row['file_path']
            cur_row['summary'] = row['summary']
            cur_row['tags'] = row['tags']
        search_result.append(cur_row)
    return search_result    

# TODO:유사도 검색 시 어울리지 않는 거 뜨는 문제 발생
def search_with_distance(query, top_k=30):
    if not query:
        return []
    df = pd.read_csv(STORAGE_FILE_PATH)
    document_text = df['text'].tolist()
    
    # 문서 임베딩 생성
    document_embeddings = embedding_model.encode(document_text, convert_to_tensor=True)
    
    # 문서 임베딩 인덱스에 추가
    dimension = document_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # L2 거리 인덱스 사용
    index.add(document_embeddings.cpu().numpy())
    
    # 쿼리 임베딩 생성
    query_embedding = embedding_model.encode([query], convert_to_tensor=True)
    
    # 유사도 계산
    D, I = index.search(query_embedding.cpu().numpy(), top_k)
    results = [(df.iloc[i]['uuid'], D[0][idx]) for idx, i in enumerate(I[0])]
    # 유사도 낮은 결과 제외
    search_result = []
    df = pd.read_csv(STORAGE_FILE_PATH)
    
    for result in results:
        uuid, distance = result
        print(distance)
        if distance > 450:
            continue
        else:
            filtered_df = df[df['uuid'] == uuid].copy()
            if not filtered_df.empty:
                for _, row in filtered_df.iterrows():
                    cur_row = {}
                    cur_row['uuid'] = row['uuid']
                    cur_row['file_path'] = row['file_path']
                    cur_row['text'] = row['text']
                    cur_row['summary'] = row['summary']
                    cur_row['tags'] = row['tags']
                search_result.append(cur_row)
    
    return search_result

def search_with_tag(tag):
    if not tag:
        return []
    # 전체 로드
    df = pd.read_csv(STORAGE_FILE_PATH)
    filtered_df = df[df['tags'].str.contains(tag, na=False)].copy()
    results = filtered_df['file_path'].tolist()
    return results