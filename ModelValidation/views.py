from django.views.generic.base import TemplateView

class ModelView(TemplateView):
    template_name = 'index.html'

from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import torch
import numpy as np

def load_yolov5_model():
    path_hubconfig = "labelingpage\yolov5"
    path_weight = "ModelValidation\Age_Grade_best.pt"

    model = torch.hub.load(path_hubconfig, 'custom',
                           path=path_weight, source='local')
    print("Class Labels:", model.names)

    return model

def process_image(image):
    return image

def save_visualized_image(image):
    # 랜덤한 파일 이름 생성 (중복 방지)
    filename = default_storage.get_available_name(os.path.join('ginseng_images', 'result.jpg'))

    # 이미지 저장
    default_storage.save(filename, image)

    # 저장된 이미지의 URL 반환
    return default_storage.url(filename)

def visualize_predictions(image, pred_boxes, pred_scores, class_labels, pred_a):
    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)

    valid_indices = [i for i in range(len(pred_scores)) if int(pred_scores[i][-1]) not in [9, 10, 11]]
    pred_boxes = pred_boxes[valid_indices]

    pred_scores = pred_scores[valid_indices]
    # 모든 박스의 x, y 좌표를 리스트로 추출
    x_coords = [box[0] for box in pred_boxes]
    y_coords = [box[1] for box in pred_boxes]
    x_max_coords = [box[2] for box in pred_boxes]
    y_max_coords = [box[3] for box in pred_boxes]

    # 가장 작은 x, y 좌표와 가장 큰 x, y 좌표를 찾음
    xmin = min(x_coords)
    ymin = min(y_coords)
    xmax = max(x_max_coords)
    ymax = max(y_max_coords)

    # b box
    draw.rectangle([xmin, ymin, xmax, ymax], outline="blue", width=5)

    # 가장 높은 확률을 갖는 클래스의 인덱스를 찾음

    max_score_index = pred_scores.argmax()
    predicted_class_index = int(pred_scores[max_score_index][-1].item())

    class_label_count = len(class_labels)


    # 예측된 클래스 인덱스가 클래스 레이블 범위를 벗어나는 경우에 대비하여 처리
    if 0 <= predicted_class_index < class_label_count:

        valid_indices = [i for i in range(len(pred_a)) if int(pred_a[i][-1]) not in [11, 10, 9]]

        filtered_pred_a = pred_a[valid_indices]

        highest_probability_index = torch.argmax(filtered_pred_a[:, -2])


        highest_probability = filtered_pred_a[highest_probability_index, -2]
        highest_probability = highest_probability * 100

        highest_probability_class_index = int(filtered_pred_a[highest_probability_index, -1].item())

        a1_name = class_labels[highest_probability_class_index]

        predicted_class_label = class_labels[predicted_class_index]
        predicted_class_score = "{:.4f}".format(float(pred_scores[max_score_index][0].item() * 100))

        font_path = "ModelValidation/static/NanumBarunGothic.ttf"
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)

        # 예측된 클래스 레이블을 이미지 위에 그림
        text = f"결과: {a1_name} (년근 확률: {highest_probability:.2f} %)"
        text_width, text_height = draw.textsize(text, font=font)
        text_x = xmin
        text_y = ymin - text_height - 5
        draw.text((text_x, text_y), text, fill="red", font=font)

    return image_copy, predicted_class_label, predicted_class_score

def index(request):
    return render(request, 'index.html')

def submit(request):
    if request.method == 'POST':
        # 사용자가 업로드한 이미지 가져오기
        image_file = request.FILES.get('image_files')

        # 이미지 파일이 존재하는 경우에만 모델 로딩 및 예측
        if image_file:
            # 모델 불러오기
            model = load_yolov5_model()

            # 이미지 처리
            image = Image.open(image_file)
            processed_image = process_image(image)

            # 모델에 이미지 적용 (예측)
            with torch.no_grad():
                results = model(processed_image)

            # 'Detections' 객체에서 예측 결과 추출
            pred_boxes = results.pred[0][:, :4]  # 예측된 bounding box 좌표
            pred_scores = results.pred[0][:, 4:5]  # 예측된 bounding box의 확률 (클래스별 확률) 왜 5부터냐면 1~4까지는 b box 좌표값임
            pred_a = results.pred[0]


            # 예측 결과가 비어있는지 확인
            if len(pred_boxes) == 0:
                # 예측 결과가 없을 경우 "검증 실패" 문구를 출력하도록 함
                return render(request, 'result.html', {'validation_failed': True})

            # 가장 높은 확률을 갖는 클래스의 인덱스를 찾음
            max_score_index = pred_scores.argmax()
            predicted_class_index = int(pred_scores[max_score_index][-1].item())

            class_labels = model.names
            class_label_count = len(class_labels)

            # 예측된 클래스 인덱스가 클래스 레이블 범위를 벗어나는 경우에 대비하여 처리
            if 0 <= predicted_class_index < class_label_count:

                valid_indices = [i for i in range(len(pred_a)) if int(pred_a[i][-1]) not in [11, 10, 9]]

                filtered_pred_a = pred_a[valid_indices]

                highest_probability_index = torch.argmax(filtered_pred_a[:, -2])

                # Get the probability of the row with the highest probability
                highest_probability = filtered_pred_a[highest_probability_index, -2]
                highest_probability = highest_probability * 100
                # Get the class index of the row with the highest probability
                highest_probability_class_index = int(filtered_pred_a[highest_probability_index, -1].item())

                a1_name = class_labels[highest_probability_class_index]


                # 시각화된 이미지 생성 및 클래스 레이블과 확률값 가져오기
                visualized_image, predicted_class_label, probability = visualize_predictions(
                                                                         processed_image,
                                                                         pred_boxes,
                                                                         pred_scores,
                                                                         class_labels,
                                                                         pred_a)

                # 시각화된 이미지를 파일로 저장
                output_path = os.path.join(settings.MEDIA_ROOT, 'ginseng_images', 'result.jpg')
                visualized_image.save(output_path)

                # 저장된 이미지의 URL 가져오기
                ginseng_images_url = os.path.join(settings.MEDIA_URL, 'ginseng_images', 'result.jpg')

                # 결과를 템플릿에 전달
                return render(request, 'result.html',
                              {'ginseng_images_url': ginseng_images_url,
                               'predicted_class_label': a1_name,
                               'predicted_class_score': highest_probability})

            return render(request, 'index.html')
