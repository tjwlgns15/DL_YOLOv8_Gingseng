import requests
from django.db.models import Max
from django.utils import timezone
from django.views.generic.base import TemplateView
from Account.models import UserInfo
from labelingpage.models import LabelingBoard, LabelingWork
from uploadpage.models import WonsiData
from django.shortcuts import render

class DataLabeling(TemplateView):
    template_name = 'data_labeling.html'

def Labeling_List(request):
    # LabelingData 모델의 모든 게시글 데이터를 가져옵니다.
    certification_list = LabelingBoard.objects.all()
    # 각 인스턴스의 연결된 테이블에서 username을 가져와서 추가합니다.
    for certification in certification_list:
        username = certification.work_num.username
        certification.username = username

    # 템플릿에 certification_list를 전달하여 렌더링합니다.
    return render(request, 'labelingboard_list.html', {'object_list': certification_list})

def index(request):
    wonsi_data = WonsiData.objects.filter(wonsi_verification=1).order_by('-image_id').first()
    image_path = wonsi_data.image_path if wonsi_data else ''
    return render(request, 'test.html', {'image_path': image_path})

def data_labeling(request):
    user_info = UserInfo.objects.get(username=request.user)
    if user_info.authority not in [2, 3, 4, 5]:
        return render(request, 'access_denied.html')
    else:
        if request.user.is_authenticated:
            username = request.user.username
            labeling_work = LabelingWork.objects.filter(username=username)
            context = {'labeling_work': labeling_work,
                       'authority': user_info.authority
                       }
            return render(request, 'data_labeling.html', context)

        else:
            return HttpResponse("로그인이 필요한 페이지입니다.")


# 모델적용 / 전역변수로,,,,,
import torch
from PIL import Image
def load_yolov5_model():
    path_hubconfig = "C:\pythonProject8\labelingpage\yolov5"
    path_weightfile = "C:\pythonProject8\labelingpage\yolov5\Object_best.pt"  # or any custom trained model

    model = torch.hub.load(path_hubconfig, 'custom',
                           path=path_weightfile, source='local')

    return model

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
        model = load_yolov5_model()

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

def get_labeling_data(request, image_id):
    data = LabelingData.objects.filter(image_id=image_id).values_list('image_id', 'head', 'body', 'leg', 'total')
    print(data)
    return JsonResponse(list(data), safe=False)


from django.http import HttpResponse, JsonResponse
import json
from .models import LabelingData


def save_coordinates(request, title):

    try:
        last_board_num = LabelingBoard.objects.aggregate(Max('board_num'))['board_num__max']
    except LabelingBoard.DoesNotExist:
        last_board_num = None

    if last_board_num is not None:
        board_num = int(last_board_num) + 1
    else:
        board_num = 1
    print(board_num)

    data_list = []
    date = timezone.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        # POST 요청에서 좌표 데이터 추출
        received_data = json.loads(request.body)
        print('received_data', received_data)

        for bboxData in received_data:
            startX = bboxData['startX']
            startY = bboxData['startY']
            endX = bboxData['startX'] + bboxData['width']
            endY = bboxData['startY'] + bboxData['height']

            data_list.append(startX)
            data_list.append(startY)
            data_list.append(endX)
            data_list.append(endY)

        # print('data_list', data_list)
        print('title', title)

        # 이미 있는 데이터 가져오기
        labeling_data_instance = LabelingData.objects.get(image_id=title)
        # 필요한 정보 수정
        labeling_data_instance.head = [data_list[0], data_list[1], data_list[2], data_list[3]]
        labeling_data_instance.body = [data_list[4], data_list[5], data_list[6], data_list[7]]
        labeling_data_instance.leg = [data_list[8], data_list[9], data_list[10], data_list[11]]
        labeling_data_instance.total = [data_list[12], data_list[13], data_list[14], data_list[15]]

        # 변경사항 저장
        labeling_data_instance.save()

        labeling_work_instance = LabelingWork.objects.get(image_id=title)

        label_post = LabelingBoard(
            board_num=board_num,
            title=title,
            create_date=date,
            state=0,
            work_num=labeling_work_instance,
        )
        label_post.save()

        username = request.user.username
        user_info = UserInfo.objects.get(username=username)
        user_info.labeling_post += 1
        user_info.save()


        # 적절한 응답을 반환 (예: 성공 메시지)
        return HttpResponse('좌표가 성공적으로 저장되었습니다.')

    # POST 요청이 아니면 405 Method Not Allowed 응답을 반환
    return HttpResponse(status=405)
