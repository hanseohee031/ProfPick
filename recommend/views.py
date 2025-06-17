# recommend/views.py

import os
import pandas as pd

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# 1) 모델별 기본 가중치 (GET 시 드래그 순서가 없을 때 사용)
default_weights = {
    'yunseo':  {'소통_잘됨':5, '참여_유도':4, '학점_잘줌':3, '친근함':2, '강의_잘함':1},
    'nari':    {'강의_잘함':5, '소통_잘됨':4, '친근함':3, '참여_유도':2, '학점_잘줌':1},
    'jaehoon': {'참여_유도':5, '학점_잘줌':4, '강의_잘함':3, '소통_잘됨':2, '친근함':1},
    'seohee':  {'학점_잘줌':5, '강의_잘함':4, '소통_잘됨':3, '참여_유도':2, '친근함':1},
}

# 2) 카테고리 키 → 화면 라벨 매핑
category_labels = {
    '소통_잘됨': '소통 잘됨',
    '참여_유도': '참여 유도',
    '학점_잘줌': '학점 잘줌',
    '친근함':   '친근함',
    '강의_잘함': '강의 잘함',
}

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

print('Loading SentenceTransformer and NN...')
sbert = SentenceTransformer('distiluse-base-multilingual-cased')

class MyNN(nn.Module):
    def __init__(self, input_size, num_classes):
        super(MyNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x

net = MyNN(sbert.get_sentence_embedding_dimension(), 6)
net.load_state_dict(torch.load('data/nn_model.pth'))
net.eval()

print('Done!')

@login_required
def recommend(request):
    """
    - GET  /recommend/                -> 모델 선택 페이지
    - GET  /recommend/?model=<name>   -> 해당 모델 드래그 우선순위 페이지
    - POST /recommend/?model=<name>   -> 해당 모델 추천 결과 페이지
    """

    # 1) 모델 파라미터가 없는 GET 요청이면 모델 선택 페이지 렌더
    if request.method == 'GET' and 'model' not in request.GET:
        return render(request, 'recommend.html')

    # 2) model 파라미터가 있는 GET/POST 요청 처리
    model = request.GET.get('model')  # 'yunseo', 'nari', 'jaehoon', 'seohee'

    # ────────────── “nari” 전용 GET 처리 ──────────────
    if request.method == 'GET' and model == 'nari':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(BASE_DIR, 'data', 'professor_recommendations.csv')
        df = pd.read_csv(csv_path)

        # 컬럼명 공백 → 언더스코어로 변경
        df.rename(columns=lambda c: c.replace(' ', '_'), inplace=True)

        # 지정한 순서대로 정렬
        desired_order = ['김은주', '양은샘', '신미영', '김유섭', '김선정', '이정근']
        df = df.set_index('교수_이름').loc[desired_order].reset_index()

        # 전체 컬럼을 리스트 of dict 형태로 변환
        records = df.to_dict(orient='records')

        return render(request, 'recommend/nari_list.html', {
            'records': records
        })
    # ──────────────────────────────────────────────────

    # ────────────── “jaehoon” 전용 GET 처리 ──────────────
    if request.method == 'GET' and model == 'jaehoon':
        return render(request, 'recommend/jaehoon_result.html', {
            'show_result': False
        })
    # ──────────────────────────────────────────────────

    # 3) 드래그 리스트에 사용할 카테고리 구성
    cats = default_weights.get(model, default_weights['yunseo'])
    categories = [
        {'key': key, 'label': category_labels[key]}
        for key in cats.keys()
    ]

    show_result = False
    recommendations = []

    # 4) POST 요청일 때만 추천 결과 계산
    if request.method == 'POST':        
        # ────────────── “jaehoon” 전용 POST 처리 ──────────────
        if model == 'jaehoon':
            # 1) 사용자 입력 텍스트 받기
            user_text = request.POST.get('user_text', '').strip()
  
            # 2) SBERT 임베딩
            embedding = sbert.encode(user_text)
            input_tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)

            # 3) NN 예측
            with torch.no_grad():
                outputs = net(input_tensor)
                probabilities = torch.softmax(outputs, dim=1).numpy().flatten()

            # 4) 교수 이름과 결과 매핑
            professor_names = ['김선정', '김유섭', '김은주', '신미영', '양은샘', '이정근']  # 모델 학습 시 사용한 순서와 일치해야 함
            recommendations = sorted(zip(professor_names, probabilities), key=lambda x: x[1], reverse=True)

            return render(request, 'recommend/jaehoon_result.html', {
                'model': model,
                'categories': categories,
                'show_result': True,
                'recommendations': recommendations,
            })
        # ──────────────────────────────────────────────────

        # 4.1) 사용자가 정렬한 우선순위 파싱
        order = request.POST.get('aspect_order', '')
        if order:
            aspects = order.split(',')
        else:
            aspects = list(default_weights[model].keys())

        # 4.2) 모델별 CSV 파일 선택
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_map = {
            'seohee':  'professor_scores_seohee.csv',
            'yunseo':  'professor_scores.csv'
        }
        csv_file = csv_map.get(model, 'professor_scores.csv')
        csv_path = os.path.join(BASE_DIR, 'data', csv_file)

        # 4.3) 점수 데이터 로드 및 컬럼명 정규화
        df = pd.read_csv(csv_path)
        df.rename(columns=lambda c: c.replace(' ', '_'), inplace=True)

        # 4.4) 각 카테고리에 대한 가중치 계산
        weights = {a: (len(aspects) - i) for i, a in enumerate(aspects)}

        # 4.5) total_score 계산
        df['total_score'] = (
            df[aspects]
              .mul([weights[a] for a in aspects], axis=1)
              .sum(axis=1)
        )

        # 4.6) 내림차순 정렬 후 추천 리스트 생성
        df_sorted = df.sort_values('total_score', ascending=False)
        recommendations = list(zip(
            df_sorted['professor'],
            df_sorted['total_score']
        ))
        show_result = True

    # 5) 드래그 화면(GET) 또는 결과 화면(POST) 렌더링
    return render(request, 'recommend/yunseo_result.html', {
        'model': model,
        'categories': categories,
        'show_result': show_result,
        'recommendations': recommendations,
    })
