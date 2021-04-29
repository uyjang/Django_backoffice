from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views.generic import ListView
from .forms import RegisterForm
from .models import Order
from django.utils.decorators import method_decorator# 클래스 뷰 안에는 클래스 뷰 기능들이 url에 접근할 수 있도록 dispatch라는 함수가 내장되어있음. 그래서 원래는 클래스 뷰 내부에 디스패치라는 함수를 만들고 그 위에 @데코레이터 로 지정을 해줘야 됨
from fcuser.decorators import login_required
from django.db import transaction
from product.models import Product
from fcuser.models import Fcuser

@method_decorator(login_required, name='dispatch')
class OrderCreate(FormView):
    # template_name = 'register_product.html' # 템플릿네임은 필요가 없는 게 상품주문화면이 따로 필요한게 아님. 상품주문은 자세히보기 페이지에서 주문이 이루어질 것이기 때문이다.
    form_class = RegisterForm
    success_url = '/product/'

    def form_valid(self, form):
        with transaction.atomic():
            prod = Product.objects.get(pk=form.data.get('product'))
            order = Order(quantity=form.data.get('quantity'), product=prod, fcuser=Fcuser.objects.get(email=self.request.session.get('user')))
            order.save() # 현재 주문이 생긴 상태
            prod.stock -= int(form.data.get('quantity')) # 주문이 생겼으면 그만큼 재고가 빠짐
            prod.save()
        return super().form_valid(form)
   

    def form_invalid(self, form):
        return redirect('/product/'+ str(form.data.get('product'))) # 수량이나 상품명 값이 없을 때 에러메시지를 띄워야 하는데 템플릿을 만들고 진행한 게 아니라서 어디에 띄워야 할 지 모르는 상태
                                                   # 그리고 폼이 유효성검사에서 유효성이 없을 때는 프로덕트(리스트)로 보낼건데 뒤에 product의 id값을 붙여줌 이렇게 하므로써 유효하지않으면 다시 해당상품의 상세페이지로 돌아오게함

    # forms.py에 있는 레지스터폼에 리퀘스트를 넣었으면 폼뷰에서도 리퀘스트를 인식할 수 있도록 만들어줘야됨
    def get_form_kwargs(self, **kwargs): # 폼을 생성할 때 어떤 인자값을 전달해서 만들 것인지 선택하는 함수 # view형태면은 get방식이라서 request가 있지만 오더크리에이트는 POST방식이라서 리퀘스트가 없다. 그래서 이 함수를 사용해서 리퀘스트를 만듦
        kw = super().get_form_kwargs(**kwargs) # 기존에 있는 함수부터 먼저 만들어주고 (kw안에는 기본적으로 폼뷰가 알아서 생성하는 인자값들을 만들어놓음)
        kw.update({'request': self.request})
        return kw

@method_decorator(login_required, name='dispatch')
class OrderList(ListView):
    template_name = 'order.html'
    context_object_name = 'order_list'

    def get_queryset(self, **kwargs):
        queryset = Order.objects.filter(fcuser__email=self.request.session.get('user'))# 모델을 이용하게 되면 다른사람의 주문정보까지 보게됨 왜냐면 모델은 데이터베이스에 연동되는 것이라 데이터베이스 자체를 불러오게돼서
        # 그래서 세션에 저장된 유저의 id값에 해당하는 정보만 가져오려고 설정
        # 쿼리셋을 이용하려면 세션이 필요하다. 세션은 리퀘스트가 필요하다. 리퀘스트 설정하기가 조금 번거롭다. 그래서 겟쿼리셋이라는 함수를 이용해서 변수가 아닌 함수로 오버라이딩을 진행
        return queryset



