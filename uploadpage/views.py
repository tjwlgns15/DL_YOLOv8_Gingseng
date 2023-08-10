import requests
import torch
from PIL import Image
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from labelingpage.views import yolov5_pred
from .models import WonsiBoard, WonsiData, GenerateId
from Account.models import UserInfo
from django.shortcuts import render, redirect
from google.cloud import storage
from django.conf import settings
from django.utils.text import slugify
import os
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
import re
from labelingpage.models import LabelingData


# 다른 인삼 선택
def increase_ginseng(request):
    if request.method == 'GET':
        ginseng_id = generate_ginseng_id()
        username = request.user.username
        user_info = UserInfo.objects.get(username=username)

        generate_id_instance = GenerateId.objects.create(
            ginseng_id=ginseng_id,
            username=user_info
        )
        generate_id_instance.save()

    return JsonResponse({'message': '인삼 ID가 성공적으로 증가되었습니다.'})

def index(request):
    all_boards = WonsiBoard.objects.all().order_by("-date")
    return render(request, 'uploadpage:wonsiboard_list.html')


def write(request):
    return render(request, 'uploadpage/uploadpage.html')

def generate_title():
    last_image_id = WonsiData.objects.aggregate(Max('image_id'))['image_id__max']
    last_ginseng_id = GenerateId.objects.aggregate(Max('ginseng_id'))['ginseng_id__max']
    if last_ginseng_id:
        ginseng_id = last_ginseng_id
    else:
        ginseng_id = generate_ginseng_id()

    if last_image_id:
        last_number = int(re.search(r'\d+', last_image_id).group())
        new_number = last_number + 1
        image_id = f'image_id_{str(new_number).zfill(6)}'

    else:
        image_id = 'image_id_000001'

    return f'{ginseng_id}_{image_id}'

def generate_image_id():
    last_image_id = WonsiData.objects.aggregate(Max('image_id'))['image_id__max']

    if last_image_id:
        last_number = int(re.search(r'\d+', last_image_id).group())
        new_number = last_number + 1
        image_id = f'image_id_{str(new_number).zfill(6)}'
    else:
        image_id = 'image_id_000001'

    return image_id


def generate_ginseng_id():
    last_ginseng_id = GenerateId.objects.aggregate(Max('ginseng_id'))['ginseng_id__max']

    if last_ginseng_id:
        last_number = int(re.search(r'\d+', last_ginseng_id).group())
        new_number = last_number + 1
        ginseng_id = f'ginseng_id_{str(new_number).zfill(6)}'
    else:
        ginseng_id = 'ginseng_id_000001'

    return ginseng_id

def create_reply(request, board_id):
    b = WonsiBoard.objects.get(wonsi_num=board_id)
    b.wonsicomments_set.create(text=request.POST['comment'], creat_date=timezone.now())
    return HttpResponseRedirect(reverse('uploadpage:detail', args=(board_id,)))

class Board_List(ListView):
    model = WonsiBoard
    ordering = ['date']
    template_name = 'uploadpage/wonsiboard_list.html'
    context_object_name = 'board_list'
    paginate_by = 5


path_hubconfig = "C:\pythonProject8\labelingpage\yolov5"
path_weightfile = "C:\pythonProject8\labelingpage\yolov5\Object_best.pt"  # or any custom trained model
model = torch.hub.load(path_hubconfig, 'custom', path=path_weightfile, source='local')


def yolov5_pred(wonsi_data):
    # 기존 데이터에서 가장 큰 label_num 가져오기
    try:
        last_label_num = LabelingData.objects.aggregate(Max('label_num'))['label_num__max']
    except LabelingData.DoesNotExist:
        last_label_num = None
    print(last_label_num)

    if last_label_num is not None:
        label_num = int(last_label_num)+1
    else:
        label_num = 1
    print(last_label_num)

    image_url = f'https://storage.googleapis.com/insam/{wonsi_data.image_id}'
    response = requests.get(image_url, stream=True)

    if response.status_code == 200:
        image_data = response.raw
        image = Image.open(image_data)
        image = image.resize((600, 750))

        # YOLOv5 모델 로드
        # model = load_yolov5_model()

        # 이미지를 모델에 전달하여 예측 수행
        with torch.no_grad():
            results = model(image)

        # 바운딩 박스 좌표 가져오기
        bboxes = results.pandas().xyxy[0].values.tolist()
        new_bboxes = [bbox[5:] + bbox[:4] for bbox in bboxes]

        head, body, leg, total = None, None, None, None

        for bbox in new_bboxes:
            if bbox[0] == 1:
                head = [int(coord) for coord in bbox[2:]]
            elif bbox[0] == 2:
                body = [int(coord) for coord in bbox[2:]]
            elif bbox[0] == 3:
                leg = [int(coord) for coord in bbox[2:]]
            elif bbox[0] == 0:
                total = [int(coord) for coord in bbox[2:]]

        insam = LabelingData(
            label_num=label_num,
            head=head,
            body=body,
            leg=leg,
            total=total,
            label_verification=0,
            image_id=wonsi_data,
        )
        insam.save()

def write_board(request):
    if request.method == 'POST':
        date = timezone.now().strftime('%Y-%m-%d')
        category_variety = request.POST.get('category_variety')
        category_age = request.POST.get('category_age')
        category_grade = request.POST.get('category_grade')
        title = generate_title()

        for image_file in request.FILES.getlist('image_files'):
            image_id_title = generate_image_id()
            while True:
                image_id = f'{image_id_title}'
                try:
                    existing_wonsi_data = WonsiData.objects.get(image_id=image_id)
                    BoardCounter.increase_image_counter()
                    image_id_title = generate_image_id()
                except ObjectDoesNotExist:
                    break

            username = request.user.username
            user_info = UserInfo.objects.get(username=username)
            user_info.upload_post += 1
            user_info.save()

            latest_ginseng_id = GenerateId.objects.filter(username=user_info).latest('ginseng_id').ginseng_id

            ginseng_info = GenerateId.objects.get(ginseng_id=latest_ginseng_id)
            last_wonsi_num = WonsiBoard.objects.aggregate(Max('wonsi_num'))['wonsi_num__max']
            wonsi_num = last_wonsi_num + 1 if last_wonsi_num is not None else 1

            wonsi_data = WonsiData.objects.create(
                image_id=image_id,
                ginseng_id=ginseng_info,
                variety=category_variety,
                age=category_age,
                grade=category_grade,
                username=user_info,
            )

            a = WonsiBoard(
                wonsi_num = wonsi_num,
                image_id = wonsi_data,
                title=title,
                date=date,
                username=user_info,
            )
            a.save()

            client = storage.Client.from_service_account_json(settings.GOOGLE_CLOUD_KEY_PATH)
            bucket_name = 'insam'
            bucket = client.get_bucket(bucket_name)
            image_blob = bucket.blob(image_id)
            image_blob.upload_from_file(image_file, content_type=image_file.content_type)

            yolov5_pred(wonsi_data)

        return HttpResponseRedirect(reverse('uploadpage:write_board'))
    else:
        user_info = UserInfo.objects.get(username=request.user)
        if user_info.authority not in [1,3,4,5]:
            return render(request, 'access_denied.html')
        else:
            username = request.user.username
            user_info = UserInfo.objects.get(username=username)
            ginseng = GenerateId.objects.filter(username=user_info).latest('ginseng_id').ginseng_id
            context = {
                'ginseng': ginseng,
                'upload_count':user_info.upload_post,
                'authority': user_info.authority
            }
            return render(request, 'uploadpage/uploadpage.html', context)



def create_generate_id(request):
    if request.method == 'POST':
        ginseng_id = generate_ginseng_id()
        username = request.user.username
        user_info = UserInfo.objects.get(username=username)

        generate_id_instance = GenerateId.objects.create(
            ginseng_id=ginseng_id,
            username=user_info
        )
        generate_id_instance.save()

        return HttpResponseRedirect(reverse('uploadpage:write_board'))

    return redirect('/home')
