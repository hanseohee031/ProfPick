from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def recommend(request):
    model = request.GET.get('model')
    professor = None

    if model == "nari":
        professor = "나리 모델의 추천 결과"
    elif model == "yunseo":
        professor = "윤서 모델의 추천 결과"
    elif model == "jaehoon":
        professor = "재훈 모델의 추천 결과"
    elif model == "seohee":
        professor = "서희 모델의 추천 결과"
    # 추후 각 모델별로 실제 추천 로직 연결

    return render(request, 'recommend.html', {'professor': professor})
