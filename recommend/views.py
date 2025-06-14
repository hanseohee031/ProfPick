import os
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def recommend(request):
    # GET/POST 양쪽에서 model 파라미터 받아오기
    model = request.GET.get('model') or request.POST.get('model')

    # 1) 공통: 카테고리 키 목록과 라벨 매핑
    aspects = ['강의_잘함', '소통_잘됨', '참여_유도', '친근함', '학점_잘줌']
    label_map = {
        '강의_잘함': '강의 잘함',
        '소통_잘됨': '소통 잘됨',
        '참여_유도': '참여 유도',
        '친근함':   '친근함',
        '학점_잘줌': '학점 잘줌',
    }

    # 2) GET → 초기화면: 드래그&드롭 리스트
    if request.method == 'GET' and model:
        # (선택) 모델별 기본초기순서 정의
        default_weights = {
            'yunseo':  {'소통_잘됨':5, '참여_유도':4, '친근함':3, '학점_잘줌':2, '강의_잘함':1},
            'jaehoon': {'강의_잘함':5, '소통_잘됨':4, '참여_유도':3, '친근함':2, '학점_잘줌':1},
            'nari':    {'친근함':5, '강의_잘함':4, '소통_잘됨':3, '참여_유도':2, '학점_잘줌':1},
            'seohee':  {'학점_잘줌':5, '강의_잘함':4, '소통_잘됨':3, '참여_유도':2, '친근함':1},
        }
        wm = default_weights.get(model, {})
        sorted_aspects = sorted(aspects, key=lambda k: wm.get(k, 0), reverse=True)
        categories = [{'key': k, 'label': label_map[k]} for k in sorted_aspects]

        return render(request, 'recommend/yunseo_result.html', {
            'categories': categories,
            'show_result': False,
            'model': model,
        })

    # 3) POST → 사용자 드래그 순서 반영해서 가중치 계산 및 추천
    if request.method == 'POST' and model:
        # 3.1) 넘어온 순서 읽기
        order_str = request.POST.get('aspect_order', '')
        order_list = [x for x in order_str.split(',') if x in aspects]
        if not order_list:
            order_list = aspects[:]

        # 3.2) 순서별 사용자 가중치 설정 (1순위:10, 2순위:5, 3순위:3, 4순위:1, 5순위:0)
        weight_values = [10, 5, 3, 1, 0]
        user_weights = {
            aspect: weight_values[idx] if idx < len(weight_values) else 0
            for idx, aspect in enumerate(order_list)
        }

        # 3.3) 원본 점수 데이터 로드
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(BASE_DIR, 'data', 'professor_scores.csv')
        df = pd.read_csv(csv_path)  # 컬럼: ['professor'] + aspects

        # 3.4) 컬럼별 가중치 곱하고 총점 계산
        weighted = df.copy()
        for asp, w in user_weights.items():
            weighted[asp] = weighted[asp] * w
        weighted['total_score'] = weighted[list(user_weights.keys())].sum(axis=1)

        # 3.5) 내림차순 정렬 후 교수님 순위 및 점수 리스트
        df_sorted = weighted.sort_values('total_score', ascending=False)
        recommendations = list(zip(df_sorted['professor'], df_sorted['total_score']))

        return render(request, 'recommend/yunseo_result.html', {
            'recommendations': recommendations,
            'show_result': True,
            'model': model,
        })

    # 4) model 파라미터가 없거나 다른 경우
    return render(request, 'recommend.html', {})
