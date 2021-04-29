from django.shortcuts import redirect
from .models import Fcuser

def login_required(function):
    def wrap(request, *args, **kwargs): # 원래 넣어야 되는 dispatch함수에는 request,*args, **kwargs라는 인자들이 들어있었으므로 여기에도 넣어줘야됨
        user = request.session.get('user')
        if user is None or not user:
            return redirect('/login')
        return function(request, *args, **kwargs)
    return wrap


def admin_required(function):
    def wrap(request, *args, **kwargs):
        user = request.session.get('user') # 세션 일때는 '' 붙이고
        if user is None or not user:
            return redirect('/')
        user = Fcuser.objects.get(email=user) # 모델일 때는 '' 안붙임
        if user.level != 'admin':
            return redirect('/')
            
        return function(request, *args, **kwargs)
    return wrap