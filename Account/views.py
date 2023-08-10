from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from .models import UserInfo
from argon2 import PasswordHasher
from django.core.exceptions import ValidationError
import re

class AccountView(TemplateView):
    template_name = 'account_test.html'

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if not username or not password1 or not password2 or not name or not email or not phone:
            error_message = "필수 정보를 입력해주세요."
            return render(request, "account_test.html", {"error": error_message, "active_tab": "signup",
                                                         "username": username, "name": name, "email": email,
                                                         "phone": phone})

        if User.objects.filter(username=username).exists():
            error_message = "이미 사용 중인 아이디입니다."
            return render(request, "account_test.html", {"error": error_message, "active_tab": "signup",
                                                         "name": name, "email": email, "phone": phone})

        if password1 != password2:
            error_message = "비밀번호가 일치하지 않습니다."
            return render(request, "account_test.html", {"error": error_message, "active_tab": "signup",
                                                         "username": username, "name": name, "email": email,
                                                         "phone": phone})

        if not re.match(r'^\d{11}$', phone):
            error_message = "유효한 핸드폰 번호를 입력해주세요. ('-' 제외, 11자리)"
            return render(request, "account_test.html", {"error": error_message, "active_tab": "signup",
                                                         "username": username, "name": name, "email": email})

        try:
            validate_password(password1)
        except ValidationError as e:
            error_message = str(e)
            return render(request, "account_test.html", {"error": error_message, "active_tab": "signup",
                                                         "username": username, "name": name, "email": email,
                                                         "phone": phone})

        user_info = UserInfo(name=name, username=username, pwd=PasswordHasher().hash(password1), email=email, phone=phone)
        user_info.save()

        user = User.objects.create_user(username=username, password=password1)

        auth.login(request, user)

        return redirect('/home/')

    return render(request, "account_test.html", {"active_tab": "signup"})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/home/')
        else:
            return render(request, 'account_test.html', {'error_login': '아이디 또는 비밀번호가 일치하지 않습니다.'})
    else:
        return render(request, 'account_test.html')

def logout(request):
    auth.logout(request)
    return redirect('/home/')
