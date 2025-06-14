# recommend/logic.py
import pandas as pd
import os

def recommend_professors(user_weights, data_path=None):
    """
    user_weights: dict, 예) {'강의잘함': 5, '소통잘됨': 3, '참여유도': 2, '친근함': 4, '학점잘줌': 1}
    data_path: CSV 파일 경로 (테스트 시 경로 지정, 실제 운영에서는 None)
    """
    # CSV 경로 자동 지정
    if data_path is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(BASE_DIR, 'data', 'professor_aspect_score.csv')
    df = pd.read_csv(data_path)

    # 교수명 컬럼 이름이 다를 수 있음 ('교수명' 또는 'professor' 등 확인)
    prof_col = '교수명' if '교수명' in df.columns else 'professor'

    aspects = ['강의잘함', '소통잘됨', '참여유도', '친근함', '학점잘줌']
    # 혹시 누락된 컬럼 있으면 필터링
    aspects = [a for a in aspects if a in df.columns]

    def calc_score(row):
        return sum(row[aspect] * user_weights.get(aspect, 0) for aspect in aspects)

    df['total_score'] = df.apply(calc_score, axis=1)
    df_sorted = df.sort_values(by='total_score', ascending=False)
    # 결과는 교수명/총점/상세 점수 포함
    result = df_sorted[[prof_col, 'total_score'] + aspects].reset_index(drop=True)
    return result
