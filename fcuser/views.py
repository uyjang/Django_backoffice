from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm
from django.contrib.auth.hashers import make_password
from .models import Fcuser
# Create your views here.

def index(request):  
    return render(request, 'index.html', {'email':request.session.get('user')})

class RegisterView(FormView): # project1에서는 전부 함수를 이용했지만 클래스뷰를 이용해서 forms.py 파일 안에도 폼을 클래스형태로 만들고 그 클래스 폼이 데이터 받고 처리하고 유효성 검증까지 완료해서 오류있으면 표시까지 해주고 데이터베이스에 저장까지 함
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = '/'

    def form_valid(self, form): # 폼에서 유효성검사를 하고 유효성검사하는 clean함수가 데이터를 저장까지 했었는데 그걸 분리해서 뷰에서 form_valid함수에 오버라이딩 한 것
        fcuser = Fcuser(
            email = form.data.get('email'),
            password = make_password(form.data.get('password')), # 비밀번호 입력 시 ***** 모양으로 나오게 만듦
            level = 'user'
        )
        fcuser.save()

        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/'
    # 로그인을 했으면 세션에 저장을 해놔야 로그인상태도 유지도 되고 쿠키에 아이디 정보가 입력돼 다음번에 들어갔을 때 더 빠른 처리가 가능하다
    def form_valid(self, form): # forms.py에서 유효성 점검이 다 끝나고 정상일 때 실행되는 함수이므로 여기다가 세션을 만들어준다. 유효성이 보장된 폼이면 세션을 만든다는 뜻
        self.request.session['user'] = form.data.get('email') # 리퀘스트 안에는 세션이 있고 세션은 여러개의 키들을 가지고 있는 데 그 중에서 user라는 키에 폼에서 가져온 이메일을 값으로 넣겠다 였었지만 register에서 유효성검사와 데이터 저장을 분리해서 이젠 그냥form.data.get('')을 통해 데이터를 가지고 오면 됨.
        return super().form_valid(form) # 그 다음 기존의 폼벨리드 함수를 다시 호출한다.

def logout(request):
    if 'user' in request.session:
        del(request.session['user'])
    return redirect('/')