"""fc_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from fcuser.views import index
from fcuser.views import RegisterView, LoginView, logout
from product.views import ProductList, ProductCreate, ProductDetail, ProductListAPI, ProductDetailAPI
from order.views import OrderCreate, OrderList 
from django.views.generic import TemplateView
from order.models import Order
import datetime
from .functions import get_exchange

# 메인홈페이지를 커스터마이징하기 위한 코드
orig_index = admin.site.index # admin.site는 장고가 자기들이 기본적으로 만들어 놓은 웹페이지 틀을 관리하기 위해 만든 패키지이고 그 안에 index라고하는 메인페이지가 있음.
                              # 근데 지금 프로젝트 바로 밑에 있는 templates폴더에 index를 복사 해왔기 때문에 settings에서 설정한 대로 프로젝트 밑에 있는 templates폴더를 먼저 뒤지고
                              # 거기에 없으면 app안에 있는 templates폴더를 뒤지게 됨. 그래서 프로젝트 밑에 templates폴더 안에 있는 index.html(현재 파일)이 우선순위로 인식됨.
                              # 그래서 내가 추가하고자 하는 정보를 넣고 return문으로 원래 orig_index를 덮어 씌움
def jang_index(request, extra_context=None):
    base_date = datetime.datetime.now() - datetime.timedelta(days=7)# 7일 전이라는 기준값 생성
    order_data = {}
    for i in range(7):
        target_dttm = base_date + datetime.timedelta(days=i)# 7일전부터 0부터 해서 6일 후의 날짜를 담고
        date_key = target_dttm.strftime('%Y-%m-%d')# 그 날짜들 보기 쉽게 형 변환 해주고
        target_date = datetime.date(target_dttm.year, target_dttm.month, target_dttm.day) #위에서 만든 0일부터 6일 후까지의 날짜를 년 월 일 별로 새롭게 date를 생성하고
        order_cnt = Order.objects.filter(register_date__date=target_date).count() # 주문 생성일(register_date)안에 있는 date에 target_dttm을 형변환한 target_data를 넣고 그날 생성된 갯수(count)를 센다
        order_data[date_key] = order_cnt
    extra_context = {
        'orders' : order_data ,
        'exchange' : get_exchange()
    }
    return orig_index(request, extra_context)
admin.site.index = jang_index # jang_index는 함수(view기능을 하는)인데 admin.site.index안에 담고 출력을하면 원래 있던 것들이 사라지고 내가 끼워넣은 것만 출력이 된다.
                                    # 이럴 때는 오리진 인덱스라고 원래 있던거에 admin.site.index(장인덱스라는 함수를 담은)를 넣어준다.


urlpatterns = [
    re_path(r'^admin/manual/$', TemplateView.as_view(template_name='admin/manual.html', extra_context={'title':'메뉴얼', 'site_title':'장의영 백오피스', 'site_header':'장의영 백오피스'})),   
    # 이거를 admin/ 위로 보낸 이유는 admin/ 아래로 들어가면 admin/ 의 하위로 들어가게 되면서 접근할 수 없게 돼버린다. 
    # 또한 지정한 템플릿은 앱에 연결이 안돼있다. 그럴때는 템플릿이 프로젝트 바로 아래에 있어야 한다.
    # 그리고 date_view처럼 어드민에서 사용 되는 view기능을 해주는 함수를 따로 안만들고 TemplateView라는 기능으로 그냥 간단하게만 처리해서 self.admin_site.each_context(request)를 활용해서 왼쪽에 보이는 메뉴들에 정보들을 못넣음. 그래서 직접 넣어야됨
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('', index),
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('product/',ProductList.as_view()),
    path('product/create/',ProductCreate.as_view()),
    path('product/<int:pk>/',ProductDetail.as_view()),
    path('order/create/',OrderCreate.as_view()),
    path('order/',OrderList.as_view()),
    path('logout/',logout),
    path('api/product/', ProductListAPI.as_view()),
    path('api/product/<int:pk>', ProductDetailAPI.as_view()),


]
