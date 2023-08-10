from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, ListView
from django.shortcuts import render
from Account.models import UserInfo
from notice.models import Notice
from uploadpage.models import WonsiBoard,WonsiData
from labelingpage.models import LabelingBoard
from questionboard.models import QuestionBoard
from django.contrib.auth.decorators import login_required
from django.db.models import Count
class HomeView(TemplateView):
    template_name = 'home/home2.html'

    @login_required(login_url='account/login/')
    def basepage(request):
        # notice
        articles = Notice.objects.order_by('-Notice_num')  # Notice_num을 기준으로 내림차순 정렬

        # 페이징
        paginator = Paginator(articles, 7)  # 페이지당 5개의 게시물
        page_number = request.GET.get('page')
        page_object = paginator.get_page(page_number)
        username = request.user.username
        user = UserInfo.objects.get(username=username)

        # questionboard
        articles = QuestionBoard.objects.order_by('-question_num')
        user = request.user.username
        username = UserInfo.objects.get(username=user)

        # 페이징
        paginator = Paginator(articles, 7)  # 페이지당 5개의 게시물
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        username = request.user.username
        user = UserInfo.objects.get(username=username)
        total_users_count = UserInfo.objects.count()
        total_gingseng_count = WonsiData.objects.count()
        total_labeling_count = LabelingBoard.objects.count()
        hello_authority = user.authority
        hello_user = f'{request.user.username}님'

        context = {
            'hello_authority': hello_authority,
            'hello_user': hello_user,
            'total_gingseng_count': total_gingseng_count,
            'total_users_count': total_users_count,
            "authority": user.authority,
            'page_object': page_object,
            'page_obj': page_obj,
            'total_labeling_count' : total_labeling_count,
        }
        return render(request, 'home/home2.html', context)



class Callection_TipsView(TemplateView):
    template_name = 'notice/callection_tips.html'

class Labelling_TipsView(TemplateView):
    template_name = 'notice/labelling_tips.html'


class NoticeView(TemplateView):
    template_name = 'notice/notice.html'
