from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.views.generic.base import TemplateView
from datetime import timedelta
from datetime import datetime
from notice.models import Notice
from adminpage.models import Admin
from notice.models import Notice
from Account.models import UserInfo


def index(request):
    articles = Notice.objects.order_by('-Notice_num')  # Notice_num을 기준으로 내림차순 정렬

    # 페이징
    paginator = Paginator(articles, 7)  # 페이지당 5개의 게시물
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    username = request.user.username
    user = UserInfo.objects.get(username=username)

    context = {
        'articles': articles,
        'page_obj': page_obj,
        'user': user,
        'authority': user.authority
    }
    return render(request, 'notice/index.html', context)

def NewView(request):
    return render(request, 'notice/notice_new.html')

def Create(request):
    title = request.GET.get('title')
    text = request.GET.get('text')
    creat_date = request.GET.get('creat_date')
    username = request.user.username
    user_info = UserInfo.objects.get(username=username)
    count = 0
    admin_id = Admin.objects.get(admin_id=user_info.username)
    article = Notice(title=title, text=text, admin_id=admin_id, creat_date=creat_date, count = count)
    article.save()

    return redirect('/home/notice/')

# def Detail(request, pk):
#     article = Notice.objects.get(pk=pk)
#     context = {
#         'article': article
#     }
#     response = render(request, 'notice/detail.html', context)
#
#     expire_date, now = datetime.now(), datetime.now()
#     expire_date += timedelta(days=1)
#     expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
#     expire_date -= now
#     max_age = expire_date.total_seconds()
#
#     cookie_value = request.COOKIES.get('count', '_')
#
#     if f'_{pk}_' not in cookie_value:
#         cookie_value += f'{pk}_'
#         response.set_cookie('count', value=cookie_value, max_age=max_age, httponly=True)
#         article.count += 1
#         article.save()
#
#     return response


def Detail(request, pk):
    article = Notice.objects.get(pk=pk)
    username = request.user.username
    user = UserInfo.objects.get(username=username)

    context = {
        'authority': user.authority,
        'user': user,
        'article': article,
    }

    if request.method == 'POST':
        # 필요한 경우 POST 요청을 처리합니다.
        pass
    else:
        # GET 요청을 처리합니다.
        cookie_value = request.COOKIES.get('count', '_')

        if f'_{pk}_' not in cookie_value:
            cookie_value += f'{pk}_'
            response = render(request, 'notice/detail.html', context)
            expire_date = datetime.now() + timedelta(days=1)
            expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
            max_age = (expire_date - datetime.now()).total_seconds()
            response.set_cookie('count', value=cookie_value, max_age=max_age, httponly=True)
            article.count += 1
            article.save()
            return response

        return render(request, 'notice/detail.html', context)

def edit(request, pk):
    article = Notice.objects.get(pk=pk)

    context = {
        'article' : article
    }
    return render(request, 'notice/edit.html', context)

def update(request,pk):
    article = Notice.objects.get(pk=pk)

    title = request.GET.get('title')
    text = request.GET.get('text')

    article.title = title
    article.text = text

    article.save()

    return redirect(f'/home/notice/{article.pk}/')

def delete(request, pk):
    article = Notice.objects.get(pk=pk)
    article.delete()

    return redirect('/home/notice/')
