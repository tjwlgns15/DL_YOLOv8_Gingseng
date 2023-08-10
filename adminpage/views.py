import ast
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from Account.models import UserInfo
from django.urls import reverse
from django.db.models import Sum
from questionboard.models import QuestionBoard,Answer
from uploadpage.models import WonsiData, WonsiBoard, WonsiComments
from labelingpage.models import LabelingBoard, LabelingComments
from adminpage.models import Admin
from notice.models import Notice
from django.conf import settings
from google.cloud import storage
from django.shortcuts import render
from collections import Counter
import json
from django.http import JsonResponse

from adminpage.models import point_A
from adminpage.models import point_B
from adminpage.models import point_C
from adminpage.models import point_D

class Admin_Home(View):
    def get(self, request):
        user_data = UserInfo.objects.values('authority').annotate(total=Count('authority'))
        user_data_json = json.dumps(list(user_data))

        user_info = UserInfo.objects.get(username=request.user)
        if user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        else:
            total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
            total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
            waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
            settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

            # 원 그래프 데이터 추가
            age_data = WonsiData.objects.values_list('age', flat=True)
            age_counts = dict(Counter(age_data))
            total = sum(age_counts.values())
            age_ratios = {age: count / total for age, count in age_counts.items()}
            age_ratios_json = json.dumps(age_ratios)

            # grade에 따른 데이터 개수 계산
            grades = WonsiData.objects.values_list('grade', flat=True).distinct()
            grade_counts = {grade: WonsiData.objects.filter(grade=grade).count() for grade in grades}
            grade_counts_json = json.dumps(grade_counts)

            today = timezone.now().date()
            # 날짜별 개수 구하기
            wonsi_data_count = WonsiBoard.objects.filter(date__gte=today - timedelta(days=6)).values('date').annotate(
                count=Count('wonsi_num'))
            labeling_data_count = LabelingBoard.objects.filter(create_date__gte=today - timedelta(days=6)).values(
                'create_date').annotate(count=Count('board_num'))

            # 날짜별 데이터를 담을 리스트를 초기화
            wonsi_data_list = []
            for data in wonsi_data_count:
                wonsi_data_list.append({
                    'date': data['date'].strftime('%Y-%m-%d'),  # 날짜 형식 변경
                    'count': data['count'],
                })

            labeling_data_list = []
            for data in labeling_data_count:
                labeling_data_list.append({
                    'date': data['create_date'].strftime('%Y-%m-%d'),  # 날짜 형식 변경
                    'count': data['count'],
                })


            context = {
                'user_data_json': user_data_json,
                'total_veri_sum': total_veri_sum,
                'total_label_sum': total_label_sum,
                'settlement_sum': settlement_sum,
                'waiting_sum': waiting_sum,
                'age_ratios_json': age_ratios_json,
                'grade_counts_json': grade_counts_json,
                'wonsi_data': json.dumps(wonsi_data_list),
                'labeling_data': json.dumps(labeling_data_list),

            }

            return render(request, 'admin_home.html', context)

    def get_grade_data(self, request):
        age = request.GET.get('age')
        grade_data = WonsiData.objects.filter(age=age).values_list('grade', flat=True)
        grade_counts = dict(Counter(grade_data))

        return JsonResponse(grade_counts)
class CommonDataMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_info = UserInfo.objects.get(username=self.request.user)
        if user_info.authority in [4, 5]:
            Point_boards_queryset = point_D.objects.all()
            Point_boards = list(Point_boards_queryset)
            waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
            settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
            total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
            total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
            context.update({
                'total_veri_sum': total_veri_sum,
                'total_label_sum': total_label_sum,
                'settlement_sum': settlement_sum,
                'waiting_sum': waiting_sum,
            })

        return context

class User_Manage(CommonDataMixin,ListView):
    model = UserInfo
    template_name = 'user_manage_list.html'

    def dispatch(self, request, *args, **kwargs):
        username = request.user
        user_info = UserInfo.objects.get(username=username)
        if not username.is_authenticated or user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        return super().dispatch(request, *args, **kwargs)


def User_index(request):
    user_info = UserInfo.objects.get(username=request.user)
    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        all_users = UserInfo.objects.order_by("-authority")
        return render(request, 'adminpage/user_manage_list.html', {'object_list': all_users})



def update_user_authority(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        authority = request.POST.get('authority')

        user = UserInfo.objects.get(username=username)

        user.authority = authority
        user.save()

        if request.method == 'POST':
            username = request.POST.get('username')
            user_info = UserInfo.objects.get(username=username)
            if user_info.authority in [4,5]:
                admin_make = Admin.objects.create(
                    admin_id=user_info.username,
                    pwd='1234'
                )
            else:
                try:
                    admin_to_delete = Admin.objects.get(admin_id=user_info.username)
                    admin_to_delete.delete()

                except ObjectDoesNotExist:
                    pass

        return HttpResponseRedirect(reverse('adminpage:user_index'))
    else:
        return render(request, 'adminpage/user_manage_list.html')


# class Wonsi_Verification(CommonDataMixin,ListView):
#     model = WonsiBoard
#
#     template_name = 'wonsi/wonsi_verification_list.html'
#     context_object_name = 'Wonsi_List'
#
#     def dispatch(self, request, *args, **kwargs):
#         username = request.user
#         user_info = UserInfo.objects.get(username=username)
#         if not username.is_authenticated or user_info.authority not in [4, 5]:
#             return render(request, 'access_denied.html')
#         return super().dispatch(request, *args, **kwargs)
#
#     def Wonsi_verification_index(request):
#         user_info = UserInfo.objects.get(username=request.user)
#         if user_info.authority not in [4, 5]:
#             return render(request, 'access_denied.html')
#         else:
#             all_boards = WonsiBoard.objects.all().order_by("-date")
#             return render(request, 'wonsi/wonsi_verification_list.html', {'all_boards': all_boards})


from django.views.generic import ListView
from django.http import HttpResponseRedirect
class Wonsi_Verification(CommonDataMixin, ListView):
    model = WonsiBoard
    template_name = 'wonsi/wonsi_verification_list.html'
    context_object_name = 'Wonsi_List'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        username = self.request.user.username
        user_info = UserInfo.objects.get(username=username)
        if not self.request.user.is_authenticated or user_info.authority not in [4, 5]:
            return render(self.request, 'access_denied.html')
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-date", "-wonsi_num")
        return queryset

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get("action")
        if action == "filter":
            state = self.request.POST.get("state")
            if state == "all":
                queryset = WonsiBoard.objects.all()
            elif state == "processing":
                queryset = WonsiBoard.objects.filter(state=0)
            elif state == "rejected":
                queryset = WonsiBoard.objects.filter(state=2)
            elif state == "approved":
                queryset = WonsiBoard.objects.filter(state=1)
            else:
                queryset = WonsiBoard.objects.all()

            paginator = Paginator(queryset, self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'page_obj': page_obj,
            }
            return render(self.request, 'wonsi/wonsi_verification_list.html', context)

        return HttpResponseRedirect(self.request.path)


def update_wonsi_verification(request):
    username = request.user.username
    user_info = UserInfo.objects.get(username=username)
    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        username = request.user.username
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
        user_info = UserInfo.objects.get(username=username)
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "filter":
                state = request.POST.get("state")
                if state == "all":
                    wonsi_boards = WonsiBoard.objects.all().order_by("-date", "-wonsi_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'Wonsi_List': wonsi_boards
                    }

                elif state == "processing":
                    wonsi_boards = WonsiBoard.objects.filter(state=0).order_by("-date", "-wonsi_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'Wonsi_List': wonsi_boards
                    }

                elif state == "rejected":
                    wonsi_boards = WonsiBoard.objects.filter(state=2).order_by("-date", "-wonsi_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'Wonsi_List': wonsi_boards
                    }

                elif state == "approved":
                    wonsi_boards = WonsiBoard.objects.filter(state=1).order_by("-date", "-wonsi_num")
                    context = {

                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'Wonsi_List': wonsi_boards
                    }

                else:
                    wonsi_boards = WonsiBoard.objects.all().order_by("-date", "-wonsi_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'Wonsi_List': wonsi_boards
                    }

                return render(request, 'wonsi/wonsi_verification_list.html', context)

            elif 'reject' in request.POST:
                wonsi_num = request.POST.get('wonsi_num')
                wonsi_board = WonsiBoard.objects.get(wonsi_num=wonsi_num)
                wonsi_data = WonsiData.objects.get(image_id=wonsi_board.image_id.image_id)
                wonsi_data.wonsi_verification = 0
                wonsi_data.save()
                wonsi_board.state = 2
                wonsi_board.save()
                return HttpResponseRedirect(f'/home/adminpage/wonsi_verification/{wonsi_num}/')



            elif 'approve' in request.POST:
                wonsi_num = request.POST.get('wonsi_num')
                wonsi_board = WonsiBoard.objects.get(wonsi_num=wonsi_num)
                wonsi_data = WonsiData.objects.get(image_id=wonsi_board.image_id.image_id)
                wonsi_data.wonsi_verification = 1
                wonsi_data.save()
                wonsi_board.state = 1
                wonsi_board.save()
                wonsi_boards = WonsiBoard.objects.filter(state=0)
                context = {

                    'total_veri_sum': total_veri_sum,
                    'total_label_sum': total_label_sum,
                    'settlement_sum': settlement_sum,
                    'waiting_sum': waiting_sum,
                    'Wonsi_List': wonsi_boards
                }

                return render(request, 'wonsi/wonsi_verification_list.html', context)

            elif 'delete' in request.POST:
                wonsi_num = request.POST.get('wonsi_num')
                wonsi_board = WonsiBoard.objects.get(wonsi_num=wonsi_num)
                wonsi_board.delete()

        # GET 요청일 때, 기본적으로 모든 게시판을 보여줌
        wonsi_boards = WonsiBoard.objects.all()
        context = {
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
            'Wonsi_List': wonsi_boards
        }
        return render(request, 'wonsi/wonsi_verification_list.html', context)


class Data_labeling_Verification(CommonDataMixin, ListView):
    model = LabelingBoard
    template_name = 'labeling/data_labeling_verification_list.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        username = request.user
        user_info = UserInfo.objects.get(username=username)
        if not username.is_authenticated or user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return LabelingBoard.objects.all().order_by("-create_date", "-board_num")


def wonsi_data_detail(request,pk):
    username = request.user.username
    user_info = UserInfo.objects.get(username=request.user)
    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        wonsi_board = WonsiBoard.objects.get(wonsi_num=pk)
        image_id = wonsi_board.image_id
        client = storage.Client.from_service_account_json(settings.GOOGLE_APPLICATION_CREDENTIALS)
        bucket = client.bucket(settings.GCP_BUCKET_NAME)
        image_url = f"https://storage.googleapis.com/insam/{image_id.image_id}"
        wonsi_data = WonsiData.objects.get(image_id= wonsi_board.image_id.image_id)
        comments_data = WonsiComments.objects.filter(wonsi_num=pk)
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

        context = {
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
            'wonsi_board':wonsi_board,
            'wonsi_data': wonsi_data,
            'image_url': image_url,
            'comments_data':comments_data
        }
        print(wonsi_data.age)
        if request.method == 'POST':
            wonsi_board = WonsiBoard.objects.get(wonsi_num=pk)

            if 'reject' in request.POST:
                wonsi_data = WonsiData.objects.get(image_id=wonsi_board.image_id.image_id)
                wonsi_num = WonsiBoard.objects.get(wonsi_num=pk)
                wonsi_data.wonsi_verification = 0
                wonsi_data.save()

                wonsi_board.state = 2
                wonsi_board.save()

            elif 'approve' in request.POST:
                wonsi_data = WonsiData.objects.get(image_id=wonsi_board.image_id.image_id)
                wonsi_data.wonsi_verification = 1
                wonsi_data.save()

                wonsi_board.state = 1
                wonsi_board.save()

            elif 'create_reply' in request.POST:
                create_date = request.POST.get('create_date')
                username = request.user.username
                user = UserInfo.objects.get(username=username)
                admin_id = Admin.objects.get(admin_id=user.username) #authority 5는 admin_id에 등록해줘야 작동함니다.
                text = request.POST.get('text')
                wonsi_num = WonsiBoard.objects.get(wonsi_num = pk)

                answer_make = WonsiComments.objects.create(
                    text=text,
                    create_date=create_date,
                    admin_id=admin_id,
                    wonsi_num= wonsi_num
                )
                answer_make.save()

                return HttpResponseRedirect(f'/home/adminpage/wonsi_verification/{wonsi_num.wonsi_num}/')

            elif 'delete_reply' in request.POST:
                comments_num = request.POST.get('comments_num')
                print(comments_num)
                admin_reply = WonsiComments.objects.get(wonsi_comments_num=comments_num)
                admin_reply.delete()
                wonsi_num = WonsiBoard.objects.get(wonsi_num=pk)

                return HttpResponseRedirect(f'/home/adminpage/wonsi_verification/{wonsi_num.wonsi_num}/')

            elif 'back' in request.POST:
                return redirect('adminpage:wonsi_verification_index')

            return redirect('adminpage:wonsi_verification_index')
        else:
            return render(request, 'wonsi/wonsi_data_detail.html', context)

def update_data_labeling_verification(request):
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
    username = request.user.username
    user_info = UserInfo.objects.get(username=request.user)
    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        if request.method == 'POST':
            action = request.POST.get("action")

            if action == "filter":
                state = request.POST.get("state")

                if state == "all":
                    labeling_boards = LabelingBoard.objects.all().order_by("-create_date", "-board_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'object_list': labeling_boards
                    }
                elif state == "processing":
                    labeling_boards = LabelingBoard.objects.filter(state=0).order_by("-create_date", "-board_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'object_list': labeling_boards
                    }
                elif state == "rejected":
                    labeling_boards = LabelingBoard.objects.filter(state=2).order_by("-create_date", "-board_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'object_list': labeling_boards
                    }
                elif state == "approved":
                    labeling_boards = LabelingBoard.objects.filter(state=1).order_by("-create_date", "-board_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'object_list': labeling_boards
                    }
                else:
                    # 잘못된 상태 값이 들어온 경우 전체 게시판을 보여줌
                    labeling_boards = LabelingBoard.objects.all().order_by("-create_date", "-board_num")
                    context = {
                        'total_veri_sum': total_veri_sum,
                        'total_label_sum': total_label_sum,
                        'settlement_sum': settlement_sum,
                        'waiting_sum': waiting_sum,
                        'object_list': labeling_boards
                    }

                return render(request, 'labeling/data_labeling_verification_list.html',context)

            elif 'reject' in request.POST:
                title = request.POST.get('title')
                labeling_board = LabelingBoard.objects.get(title=title)
                board_num = labeling_board.board_num
                labeling_data = LabelingData.objects.get(image_id=labeling_board.title)
                labeling_data.label_verification = 0
                labeling_data.save()

                labeling_board.state = 2
                labeling_board.save()

                labeling_work = LabelingWork.objects.get(image_id=labeling_board.title)
                labeling_work.label_verification = 0
                labeling_work.save()

                return HttpResponseRedirect(f'/home/adminpage/data_labeling_verification/{board_num}/')

            elif 'approve' in request.POST:
                title = request.POST.get('title')
                labeling_board = LabelingBoard.objects.get(title=title)
                labeling_data = LabelingData.objects.get(image_id=labeling_board.title)
                labeling_data.label_verification = 1
                labeling_data.save()

                labeling_board.state = 1
                labeling_board.save()
                labeling_boards = LabelingBoard.objects.filter(state=0)

                labeling_work = LabelingWork.objects.get(image_id=labeling_board.title)
                labeling_work.label_verification = 1
                labeling_work.save()

                context = {
                    'total_veri_sum': total_veri_sum,
                    'total_label_sum': total_label_sum,
                    'settlement_sum': settlement_sum,
                    'waiting_sum': waiting_sum,
                    'object_list': labeling_boards
                }

                return render(request, 'labeling/data_labeling_verification_list.html', context)

            elif 'delete' in request.POST:
                board_num = request.POST.get('board_num')
                labeling_board = LabelingBoard.objects.get(board_num=board_num)
                labeling_board.delete()

                labeling_work = LabelingWork.objects.get(work_num=labeling_board.work_num)
                labeling_work.delete()

            elif 'create_reply' in request.POST:
                board_num = request.POST.get('board_num')
                labeling_board = LabelingBoard.objects.get(board_num=board_num)
                create_date = request.POST.get('create_date')
                username = request.user.username
                user = UserInfo.objects.get(username=username)
                admin_id = Admin.objects.get(admin_id=user.username)  # authority 5는 admin_id에 등록해줘야 작동함니다.
                text = request.POST.get('text')
                board_num = LabelingBoard.objects.get(board_num=board_num)

                answer_make = LabelingComments.objects.create(
                    text=text,
                    create_date=create_date,
                    admin_id=admin_id,
                    board_num=board_num
                )
                answer_make.save()

                return HttpResponseRedirect(f'/home/adminpage/data_labeling_verification/{board_num.board_num}/')

            elif 'delete_reply' in request.POST:
                board_num = request.POST.get('board_num')
                labeling_board = LabelingBoard.objects.get(board_num=board_num)
                comments_num = request.POST.get('comments_num')
                admin_reply = LabelingComments.objects.get(labeling_comments_num=comments_num)
                admin_reply.delete()
                board_num = LabelingBoard.objects.get(board_num=board_num)


                return HttpResponseRedirect(f'/home/adminpage/data_labeling_verification/{board_num.board_num}/')

            elif 'back' in request.POST:
                board_num = request.POST.get('board_num')
                labeling_board = LabelingBoard.objects.get(board_num=board_num)
                return redirect('adminpage:data_labeling_verification_index')

            return redirect('adminpage:data_labeling_verification_index')
        else:
            return render(request, 'adminpage/labeling/data_labeling_verification_list.html')

def labeling_data_detail(request, pk):
    labeling_board = LabelingBoard.objects.get(board_num=pk)
    image_id = labeling_board.title
    work_id = labeling_board.work_num.username
    state = labeling_board.state
    image_url = f"https://storage.googleapis.com/insam/{image_id}"
    comments_data = LabelingComments.objects.filter(board_num=pk)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
    try:
        labeling_data = LabelingData.objects.get(image_id=image_id)
        head_list = ast.literal_eval(labeling_data.head)
        body_list = ast.literal_eval(labeling_data.body)
        leg_list = ast.literal_eval(labeling_data.leg)
        totla_list = ast.literal_eval(labeling_data.total)
        bbox_coords = [
            list(map(int, head_list)),
            list(map(int, body_list)),
            list(map(int, leg_list)),
            list(map(int, totla_list))
        ]
    except LabelingData.DoesNotExist:
        # 이미지에 해당하는 bbox 정보가 없는 경우 처리
        bbox_coords = []

    context = ({
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
        'comments_data': comments_data,
        'labeling_board': labeling_board,
        'image_id': image_id,
        'work_id': work_id,
        'state': state,
        'image_url': image_url,
        'bbox_coords': bbox_coords,
    })

    return render(request, 'labeling/data_labeling_detail.html', context)


def image_with_bbox(request, image_id):

    image_blob_name = image_id
    # 이미지 다운로드
    image_url = f'https://storage.googleapis.com/insam/{image_blob_name}'
    print(image_url)
    # bbox 정보 가져오기
    try:
        labeling_data = LabelingData.objects.get(image_id=image_blob_name)
        head_list = ast.literal_eval(labeling_data.head)
        body_list = ast.literal_eval(labeling_data.body)
        leg_list = ast.literal_eval(labeling_data.leg)
        totla_list = ast.literal_eval(labeling_data.total)
        bbox_coords = [
            list(map(int, head_list)),
            list(map(int, body_list)),
            list(map(int, leg_list)),
            list(map(int, totla_list))
        ]
    except LabelingData.DoesNotExist:
        # 이미지에 해당하는 bbox 정보가 없는 경우 처리
        bbox_coords = []

    context = {
        'image_url': image_url,
        'bbox_coords': bbox_coords,
    }
    return render(request, 'labeling/data_labeling_detail.html', context)



from django.shortcuts import render
from labelingpage.models import LabelingData, LabelingWork
from django.db.models import Count

from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render


def assignment_view(request):
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
    total_image_ids = LabelingData.objects.all().count()
    total_assigned_image_ids_count = LabelingWork.objects.all().count()
    total_unassigned_image_ids_count = total_image_ids - total_assigned_image_ids_count

    assigned_image_ids = LabelingWork.objects.values_list('image_id', flat=True)

    # WonsiData에서 wonsi_verification = 1 인 것만 필터링
    assigned_wonsi_ids = WonsiData.objects.filter(wonsi_verification=0).values_list('image_id', flat=True)

    # 할당된 Wonsi ID를 할당되지 않은 이미지 ID 목록에서 제외
    unassigned_image_ids = LabelingData.objects.exclude(image_id__in=assigned_image_ids).exclude(image_id__in=assigned_wonsi_ids).values_list('image_id', flat=True)
    unassigned_image_ids_count = unassigned_image_ids.count()
    # LabelingWork 테이블에서 작업자별 할당된 image_id 개수 구하기
    assigned_image_counts = LabelingWork.objects.values('username').annotate(count=Count('image_id'))

    # 작업자 이름 목록 가져오기
    usernames = UserInfo.objects.values_list('username', flat=True)

    # 검증 안 된 labeling_data
    non_verification = LabelingWork.objects.filter(label_verification=0)

    # 작업자별 할당된 이미지 ID 개수를 딕셔너리로 저장
    username_count_dict = {}
    for entry in non_verification.values('username').annotate(username_count=Count('username')):
        username = entry['username']
        count = entry['username_count']
        username_count_dict[username] = count

    # 할당된 데이터 가져오기
    assigned_data = LabelingWork.objects.all()

    context = {
        'total_image_ids': total_image_ids,
        'totla_unassigned_image_ids_count' : total_unassigned_image_ids_count,
        'unassigned_image_ids_count': unassigned_image_ids_count,
        'unassigned_image_ids': unassigned_image_ids,
        'usernames': usernames,
        'assigned_data': assigned_data,
        'username_count_dict': username_count_dict,
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
    }

    return render(request, 'labeling/data_assignment.html', context)

def assign_data(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        image_id = request.POST.get('image_id')

        # 이미지 ID에 해당하는 WonsiData 모델 인스턴스 가져오기
        wonsi_data_instance = get_object_or_404(WonsiData, image_id=image_id)

        # UserInfo 테이블에서 해당 username에 해당하는 인스턴스 가져오기
        user_instance = get_object_or_404(UserInfo, username=username)

        # LabelingWork 테이블에 작업자에게 이미지 ID 할당하기
        work_assignment = LabelingWork(username=user_instance, image_id=wonsi_data_instance, label_verification=0)
        work_assignment.save()

    return HttpResponseRedirect(reverse('adminpage:assignment_view'))



from django.core.paginator import Paginator

def notice_index(request):
    user_info = UserInfo.objects.get(username=request.user)

    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        articles = Notice.objects.order_by('-Notice_num')

        # 페이징
        paginator = Paginator(articles, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        username = request.user.username
        user = UserInfo.objects.get(username=username)
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

        context = {
            'page_obj': page_obj,  # articles 대신 page_obj 사용
            'user': user,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
        }
        return render(request, 'noticeadmin/notice_admin_index.html', context)


def notice_NewView(request):
    user_info = UserInfo.objects.get(username=request.user)

    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

        context = {
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
        }
        return render(request, 'noticeadmin/notice_admin_notice.html', context)

def notice_Create(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('adminpage:notice_Create'))
    else:
        title = request.GET.get('title')
        text = request.GET.get('text')
        creat_date = request.POST.get('creat_date')
        username = request.user.username
        user_info = UserInfo.objects.get(username=username)
        count = 0
        admin_id = Admin.objects.get(admin_id=user_info.username)
        article = Notice(title=title, text=text, admin_id=admin_id, creat_date=creat_date, count=count)
        article.save()

        return HttpResponseRedirect(reverse('adminpage:notice_index'))
def notice_Detail(request, pk):
    article = Notice.objects.get(pk=pk)
    username = request.user.username
    user = UserInfo.objects.get(username=username)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

    context = {
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
        'user': user,
        'article': article,
    }

    if request.method == 'POST':
        pass
    else:
        cookie_value = request.COOKIES.get('count', '_')
        if f'_{pk}_' not in cookie_value:
            cookie_value += f'{pk}_'
            response = render(request, 'noticeadmin/notice_admin_detail.html', context)
            from datetime import datetime
            from datetime import timedelta
            expire_date = datetime.now() + timedelta(days=1)
            expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
            max_age = (expire_date - datetime.now()).total_seconds()
            response.set_cookie('count', value=cookie_value, max_age=max_age, httponly=True)
            article.count += 1
            article.save()
            return response

        return render(request, 'noticeadmin/notice_admin_detail.html', context)

def notice_edit(request, pk):
    article = Notice.objects.get(pk=pk)

    context = {
        'article': article
    }

    return render(request, 'noticeadmin/notice_admin_edit.html', context)

def notice_update(request,pk):
    article = Notice.objects.get(pk=pk)
    title = request.GET.get('title')
    text = request.GET.get('text')
    article.title = title
    article.text = text
    article.save()

    return HttpResponseRedirect(f'/home/adminpage/adminnotice/{article.pk}/')

def notice_delete(request, pk):
    article = Notice.objects.get(pk=pk)
    article.delete()

    return HttpResponseRedirect('/home/adminpage/adminnotice/')



def questionboard_index(request):
    user_info = UserInfo.objects.get(username=request.user)

    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        articles = QuestionBoard.objects.all().order_by('-question_num')  # id 필드를 기준으로 내림차순 정렬
        user = request.user.username
        username = UserInfo.objects.get(username=user)

        # 페이징
        paginator = Paginator(articles, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

        context = {
            'page_obj': page_obj,
            'authority': username.authority,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
        }

        return render(request, 'questionboardadmin/questionboard_admin_index.html', context)


def questionboard_increase_id():
    last_answer = Answer.objects.last()

    if last_answer:
        return last_answer.id + 1
    else:
        return 1

def questionboard_Detail(request, pk):
    user_info = UserInfo.objects.get(username=request.user)

    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        article = QuestionBoard.objects.get(pk=pk)
        username = request.user.username
        user = UserInfo.objects.get(username=username)
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

        context = {
            'user': user,
            'article': article,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'settlement_sum': settlement_sum,
            'waiting_sum': waiting_sum,
        }

        if request.method == 'POST':
            if 'create' in request.POST:
                # 댓글 작성 코드
                create_date = request.POST.get('create_date')
                username = request.user.username
                user = UserInfo.objects.get(username=username)
                admin_id = Admin.objects.get(admin_id=user.username)
                text = request.POST.get('text')

                answer_make = Answer.objects.create(
                    question_num=QuestionBoard.objects.get(pk=pk),
                    text=text,
                    create_date=create_date,
                    admin_id=admin_id
                )
                answer_make.save()

                return redirect(f'/home/adminpage/questionboardadmin/{article.pk}/')

            elif 'delete' in request.POST:
                # 댓글 삭제 코드
                answer_id = request.POST.get('answer_id')
                answer = Answer.objects.get(id=answer_id)
                answer.delete()
                return redirect(f'/home/adminpage/questionboardadmin/{article.pk}/')

        else:
            # GET 요청 처리
            cookie_value = request.COOKIES.get('count', '_')

            if f'_{pk}_' not in cookie_value:
                cookie_value += f'{pk}_'
                from datetime import timedelta
                from datetime import datetime
                expire_date = datetime.now() + timedelta(days=1)
                expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
                max_age = (expire_date - datetime.now()).total_seconds()

                # 쿠키 설정
                response = render(request, 'questionboardadmin/questionboard_admin_detail.html', context)
                response.set_cookie('count', value=cookie_value, max_age=max_age, httponly=True)

                # 조회수 증가
                article.count += 1
                article.save()

                return response

        return render(request, 'questionboardadmin/questionboard_admin_detail.html', context)


def questionboard_delete(request, pk):
    article = QuestionBoard.objects.get(pk=pk)
    article.delete()

    return redirect('/home/adminpage/questionboardadmin/')


def questionboard_detail_answer(request, pk):
    article = QuestionBoard.objects.get(question_num=pk)

    context = {'article': article}

    return render(request, 'questionboardadmin/questionboard_admin_detail.html', context)

def questionboard_Create_answer(request):
    question_num = request.POST.get('question_num')
    text = request.POST.get('text')
    create_date = request.POST.get('create_date')
    admin_id = Admin.objects.get(admin_id='whalwjd')
    articles = QuestionBoard(text=text, admin_id=admin_id, creat_date=create_date, question_num=question_num)
    articles.save()

    return redirect('questionboardadmin:questionboard_detail')

## 포인트

class Point_change(CommonDataMixin,ListView):
    model = point_C
    template_name = 'point/Point_change.html'

    def dispatch(self, request, *args, **kwargs):
        username = request.user
        user_info = UserInfo.objects.get(username=username)
        if not username.is_authenticated or user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        return super().dispatch(request, *args, **kwargs)

def point_change_form(request):
    if request.method == 'POST':
        point_version = request.POST.get('point_ID')
        point_pay = request.POST.get('name')
        current_date = timedelta.today()

        # Create a new point_C instance and save it to the database
        point_c = point_C(point_version=point_version, point_pay=point_pay, point_date=current_date)
        point_c.save()


        # Redirect to the 'point_change_form' URL pattern using the correct name
        return redirect('adminpage:point_change_form')
    Point_boards_queryset = point_D.objects.all()
    Point_boards = list(Point_boards_queryset)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

    context = {
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
        'Point_boards': Point_boards,
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,

    }
    return render(request, 'point/Point_change.html', context)


class Account_book(ListView):
    model = point_D
    template_name = 'point/account_book.html'

    def dispatch(self, request, *args, **kwargs):
        username = request.user
        user_info = UserInfo.objects.get(username=username)
        if not username.is_authenticated or user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        return super().dispatch(request, *args, **kwargs)


def show_point_d_list(request):
    # Retrieve a list of rows where money_a is 1
    point_d_list = point_D.objects.filter(money_a=2)
    Point_boards_queryset = point_D.objects.all()
    Point_boards = list(Point_boards_queryset)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']

    context = {
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
        'Point_boards': Point_boards,
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,
        'point_d_list': point_d_list,
    }
    return render(request, 'point/account_book.html', context)


def show_point_d_list(request):
    point_d_list = point_D.objects.filter(money_a=2)
    Point_boards_queryset = point_D.objects.all()
    Point_boards = list(Point_boards_queryset)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
    user_info = UserInfo.objects.get(username=request.user)

    context = {
        'settlement_sum': settlement_sum,
        'waiting_sum': waiting_sum,
        'Point_boards': Point_boards,
        'total_veri_sum': total_veri_sum,
        'total_label_sum': total_label_sum,
        'point_d_list': point_d_list,

    }
    return render(request, 'point/account_book.html', context)

class Point_settlement(ListView):
    model = point_D
    template_name = 'point/Point_settlement_list.html'

    def dispatch(self, request, *args, **kwargs):
        username = request.user
        user_info = UserInfo.objects.get(username=username)
        if not username.is_authenticated or user_info.authority not in [4, 5]:
            return render(request, 'access_denied.html')
        return super().dispatch(request, *args, **kwargs)

def Point_settlement_index(request):
    waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
    settlement_list = point_D.objects.all()
    user_info = UserInfo.objects.get(username=request.user)

    if user_info.authority not in [4, 5]:
        return render(request, 'access_denied.html')
    else:
        Point_boards_queryset = point_D.objects.all()
        Point_boards = list(Point_boards_queryset)
        total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
        total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
        waiting_sum = point_D.objects.filter(money_a=0).aggregate(sum=Sum('money_Payments'))['sum']
        settlement_sum = point_D.objects.filter(money_a=2).aggregate(sum=Sum('money_Payments'))['sum']
        context={
            'settlement_sum':settlement_sum,
            'waiting_sum':waiting_sum,
            'Point_boards': Point_boards,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,

        }
        print(Point_boards)
        return render(request, 'point/Point_settlement_list.html', context)

def update_data_Point_settlement(request):
    if request.method == 'POST':
        money_num = request.POST.get('money_num')
        point_d = point_D.objects.get(money_num=money_num)

        if 'reject' in request.POST:
            point_d.money_a = 1
            point_d.save()

        elif 'approve' in request.POST:
            point_d.money_a = 2
            point_d.save()

        return redirect('adminpage:Point_settlement_list')
    else:
        return render(request, 'adminpage/point/Point_settlement_list.html')



def Point_settlement_List(request):
    username = request.user.username
    print(username)
    settlement_list = point_D.objects.all()
    for settlement in settlement_list:
        user_name = settlement.point_num.user_name
        settlement.user_name = user_name

    return render(request, 'Point_settlement_list.html', {'object_list': settlement_list})
