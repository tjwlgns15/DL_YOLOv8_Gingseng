from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
import cv2
from ultralytics import YOLO
from Account.models import UserInfo
from django.urls import reverse
from PIL import Image


def yolov8_main(request):
    user = request.user.username
    username = UserInfo.objects.get(username=user)

    context = {
        'authority': username.authority
    }
    return render(request,'yolov8/yolov8_main.html',context)

def yolov8_model(request):
    user = request.user.username
    username = UserInfo.objects.get(username=user)

    if request.method == 'POST':
        image_file = request.FILES.get('image_files')
        image = Image.open(image_file)

        # 모델 소환
        yolov8_model = YOLO('yolov8/v8.pt')

        # 모델 예측 저장
        predict_yolov8_model = yolov8_model.predict(image, save=False)

        # 모델 예측결과 추출
        for result in predict_yolov8_model:
            label_score = result.boxes.conf  # 박스별 항목 점수
            label_name = result.boxes.cls   # 박스별 항목 이름

        # 확률에 따라서 박스의 위치가 변함 and 가끔씩 두개씩 잡는것도 있음 => 년근 라벨링 추출 0~8번까지
        lab_loc = [i for i, num in enumerate(label_name) if num <= 8]

        if len(lab_loc) == 0:
            return render(request, 'yolov8/prediction_modal.html', {'validation_failed': True})

        # 박스를 두 개 잡을 경우 확률이 더 높은 애를 찾아가야 함
        if len(lab_loc) == 2:
            first_score = label_score[lab_loc[0]]  # 해당 위치에 있는 확률을 가져옴
            second_score = label_score[lab_loc[1]]

            if first_score.item() >= second_score.item():
                final_score = first_score
                final_label = label_name[lab_loc[0]]
            else:
                final_score = second_score
                final_label = label_name[lab_loc[1]]
        elif len(lab_loc) == 1:
            final_score = label_score[lab_loc[0]]
            final_label = label_name[lab_loc[0]]
        else:
            final_score = '잘못된 이미지'
            final_label = '잘못된 이미지'

        predict_score = round(final_score.item(), 2)
        score_name = f'{predict_score * 100}%'

        predict_label = int(final_label.item())
        if predict_label == 0:
            label_name = '4년 대'
        elif predict_label == 1:
            label_name = '4년 중'
        elif predict_label == 2:
            label_name = '4년 소'
        elif predict_label == 3:
            label_name = '5년 대'
        elif predict_label == 4:
            label_name = '5년 중'
        elif predict_label == 5:
            label_name = '5년 소'
        elif predict_label == 6:
            label_name = '6년 대'
        elif predict_label == 7:
            label_name = '6년 중'
        elif predict_label == 8:
            label_name = '6년 소'
        else:
            label_name = "알 수 없음"

        final_predict = f'해당 인삼은 {score_name} 확률로 {label_name}로 예측되었습니다.'

        prediction_results = {
            'label_name': label_name,
            'score_name': score_name,
            'final_predict': final_predict,
        }

        return render(request, 'yolov8/prediction_modal.html', prediction_results)
    else:
        user_info = UserInfo.objects.get(username=request.user)
        if user_info.authority not in [1, 3, 4, 5]:
            return render(request, 'access_denied.html')
        else:
            username = request.user.username
            user_info = UserInfo.objects.get(username=username)
            context = {
                'authority': user_info.authority
            }
            return render(request, 'yolov8/yolov8_main.html', context)