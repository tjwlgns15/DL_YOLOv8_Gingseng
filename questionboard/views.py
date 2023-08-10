from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from adminpage.models import Admin
from questionboard.models import QuestionBoard, Answer
from Account.models import UserInfo
from datetime import datetime, timedelta
from django.urls import reverse
from django.core.paginator import Paginator

id=1
def index(request):
    articles = QuestionBoard.objects.order_by('-question_num')
    user = request.user.username
    username = UserInfo.objects.get(username=user)

    # 페이징
    paginator = Paginator(articles, 7)  # 페이지당 5개의 게시물
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'authority': username.authority
    }
    return render(request, 'questionboard/index.html', context)
def NewView(request):
    return render(request, 'questionboard/qutionboard_new.html')

def Create(request):
    title = request.GET.get('title')
    text = request.GET.get('text')
    create_date = request.GET.get('create_date')
    username = request.user.username
    user_info = UserInfo.objects.get(username=username)
    count = 0
    username = user_info
    article = QuestionBoard(title=title, text=text, count=count, username=username, create_date=create_date)
    article.save()

    return redirect('/home/questionboard/')

def increase_id():
    last_answer = Answer.objects.last()
    if last_answer:
        return last_answer.id + 1
    else:
        return 1

def Detail(request, pk):
    article = QuestionBoard.objects.get(pk=pk)
    username = request.user.username
    user = UserInfo.objects.get(username=username)

    context = {
        'authority': user.authority,
        'user': user,
        'article': article,
    }
    print(user.username)

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

            return redirect(f'/home/questionboard/{article.pk}/')

        elif 'delete' in request.POST:
            # 댓글 삭제 코드
            answer_id = request.POST.get('answer_id')
            answer = Answer.objects.get(id=answer_id)
            answer.delete()
            return redirect(f'/home/questionboard/{article.pk}/')

    else:
        # GET 요청 처리
        cookie_value = request.COOKIES.get('count', '_')

        if f'_{pk}_' not in cookie_value:
            cookie_value += f'{pk}_'
            expire_date = datetime.now() + timedelta(days=1)
            expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
            max_age = (expire_date - datetime.now()).total_seconds()

            # 쿠키 설정
            response = render(request, 'questionboard/detail.html', context)
            response.set_cookie('count', value=cookie_value, max_age=max_age, httponly=True)

            # 조회수 증가
            article.count += 1
            article.save()

            return response

    return render(request, 'questionboard/detail.html', context)


def edit(request, pk):
    article = QuestionBoard.objects.get(pk=pk)

    context = {
        'article' : article
    }
    return render(request, 'questionboard/edit.html', context)

def update(request,pk):
    article = QuestionBoard.objects.get(pk=pk)

    title = request.GET.get('title')
    text = request.GET.get('text')

    article.title = title
    article.text = text

    article.save()

    return redirect(f'/home/questionboard/{article.pk}/')

def delete(request, pk):
    article = QuestionBoard.objects.get(pk=pk)
    article.delete()

    return redirect('/home/questionboard/')


def detail_answer(request, pk):
    article = QuestionBoard.objects.get(question_num=pk)
    context = {
        'article': article
    }
    return render(request, 'questionboard/detail.html', context)

def Create_answer(request):
    question_num = request.POST.get('question_num')
    text = request.POST.get('text')
    create_date = request.POST.get('create_date')
    admin_id = Admin.objects.get(admin_id='whalwjd')
    articles = QuestionBoard(text=text, admin_id=admin_id, creat_date=create_date, question_num=question_num)
    articles.save()

    return redirect('questionboard:detail')

