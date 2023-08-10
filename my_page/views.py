from django.views.generic.base import TemplateView
from django.views.generic import DetailView, ListView
from django.shortcuts import render
from Account.models import UserInfo
from adminpage.models import point_A, point_D
from uploadpage.models import WonsiBoard,WonsiData,WonsiComments
from labelingpage.models import LabelingBoard,LabelingWork,LabelingComments,LabelingData
from questionboard.models import QuestionBoard
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import ast
from django.db.models import Sum
from django.utils import timezone
class MysiteView(ListView):

    model = WonsiBoard
    template_name = 'my_page/my_page.html'

    def my_page(request):
         user = request.user
         user_info = UserInfo.objects.get(username=user.username)
         wonsi_objects = WonsiBoard.objects.filter(username=user_info.username)
         question_objects = QuestionBoard.objects.filter(username=user_info.username)
         upload_posts_count = user_info.upload_post
         labeling_posts_count = user_info.labeling_post
         question_posts_count = user_info.question_post
         wonsi_num = list(wonsi_objects.values_list('wonsi_num', flat=True))
         wonsi_comments_objects = WonsiComments.objects.filter(wonsi_num__in=wonsi_num)

         labeling_objects = LabelingWork.objects.filter(username=user_info.username)
         work_num = labeling_objects.values_list('work_num', flat=True)
         label_c_objects = LabelingBoard.objects.filter(work_num__in=work_num)
         labeling_comments_objects = LabelingComments.objects.filter(board_num__in=label_c_objects)

         wonsi_verification = WonsiData.objects.filter(username=user_info.username)
         real_wonsi_verification = wonsi_verification.filter(wonsi_verification=1).count

         label_verification = LabelingWork.objects.filter(username=user_info.username)
         real_label_verification = label_verification.filter(label_verification=1).count



         point_A_user = point_A.objects.get(user_name=user)
         remaining_points = point_A_user.remaining_points

         waiting_sum = point_D.objects.filter(user_name=user_info.username, money_a = 0).aggregate(sum=Sum('money_Payments'))['sum']
         context = {
             'label_c_objects':label_c_objects,
             'labeling_comments_objects':labeling_comments_objects,
             'user_info': user_info,
             'upload_posts_count': upload_posts_count,
             'labeling_posts_count': labeling_posts_count,
             'question_posts_count': question_posts_count,
             'wonsi_objects':wonsi_objects,
             'labeling_objects':labeling_objects,
             'question_objects':question_objects,
             'authority': user_info.authority,
             'real_wonsi_verification': real_wonsi_verification,
             'real_label_verification': real_label_verification,
             'remaining_points': remaining_points,
             'waiting_sum': waiting_sum,
         }

         return render(request, 'my_page/my_page.html', context)


def add_payment(request):
    user = request.user
    user_info = UserInfo.objects.get(username=user.username)
    current_time = timezone.now()
    if request.method == 'POST':
        money_payments = request.POST.get("money-payments")

        # Create a new entry in point_D table
        point_d = point_D(
            user_name=user_info,
            money_Payments=money_payments,
            money_date= current_time,
            money_a=0  # Set money_a to 0
        )
        point_d.save()

        return HttpResponseRedirect(reverse('my_page:my_page_a'))

    return render(request, 'my_page/my_page.html')
def wonsi_data_detail_my_page(request,pk):
    user = request.user
    user_info = UserInfo.objects.get(username = user.username)
    wonsi_board = WonsiBoard.objects.get(wonsi_num=pk)
    image_id = wonsi_board.image_id
    image_url = f"https://storage.googleapis.com/insam/{image_id.image_id}"
    wonsi_data = WonsiData.objects.get(image_id= wonsi_board.image_id.image_id)
    wonsi_objects = WonsiBoard.objects.filter(username=user_info.username)
    try:
        wonsi_comments = WonsiComments.objects.filter(wonsi_num=pk)
        context = {
            'wonsi_comments':wonsi_comments,
            'authority':user_info.authority,
            'wonsi_objects':wonsi_objects,
            'wonsi_board':wonsi_board,
            'wonsi_data': wonsi_data,
            'image_url': image_url,
        }
    except ObjectDoesNotExist:
        context = {
            'authority': user_info.authority,
            'wonsi_objects': wonsi_objects,
            'wonsi_board': wonsi_board,
            'wonsi_data': wonsi_data,
            'image_url': image_url,
        }

    return render(request, 'my_page/wonsi_data_detail_my_page.html', context)

def data_labeling_detail_my_page(request, pk):
    user = request.user
    user_info = UserInfo.objects.get(username=user.username)
    labeling_board = LabelingBoard.objects.get(board_num=pk)
    image_id = labeling_board.title
    work_id = labeling_board.work_num.username
    state = labeling_board.state
    image_url = f"https://storage.googleapis.com/insam/{image_id}"
    comments_data = LabelingComments.objects.filter(board_num=pk)
    total_veri_sum = WonsiData.objects.aggregate(Sum('wonsi_verification'))['wonsi_verification__sum']
    total_label_sum = LabelingData.objects.aggregate(Sum('label_verification'))['label_verification__sum']
    unpaid_point = 'unpaid'
    paid_point = 'paid'
    labeling_objects = LabelingWork.objects.filter(username=user_info.username)

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
    try:
        labeling_comments = LabelingComments.objects.filter(board_num=pk)
        context = ({
            'labeling_comments':labeling_comments,
            'labeling_objects': labeling_objects,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'unpaid_point': unpaid_point,
            'paid_point': paid_point,
            'comments_data': comments_data,
            'labeling_board': labeling_board,
            'image_id': image_id,
            'work_id': work_id,
            'state': state,
            'image_url': image_url,
            'bbox_coords': bbox_coords,
            'authority': user_info.authority,
        })
    except ObjectDoesNotExist:
        context = ({
            'labeling_objects': labeling_objects,
            'total_veri_sum': total_veri_sum,
            'total_label_sum': total_label_sum,
            'unpaid_point': unpaid_point,
            'paid_point': paid_point,
            'comments_data': comments_data,
            'labeling_board': labeling_board,
            'image_id': image_id,
            'work_id': work_id,
            'state': state,
            'image_url': image_url,
            'bbox_coords': bbox_coords,
        })

    return render(request, 'my_page/data_labeling_detail_my_page.html', context)