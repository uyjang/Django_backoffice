from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from .models import Product
from .forms import RegisterForm
from order.forms import RegisterForm as OrderForm
from django.utils.decorators import method_decorator
from fcuser.decorators import admin_required
from fcuser.models import Fcuser
from rest_framework import generics
from rest_framework import mixins
from .serializers import ProductSerializer
# Create your views here.

class ProductListAPI(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductDetailAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs) # list와 유일한 차이점은 url 지정하는 곳에서 pk를 지정해야 한다는 것


class ProductList(ListView): # 리스트 뷰는 별도의 폼을 만들지 않는다.
    model = Product # 어떤 모델의 리스트를 조회할 것인 지 지정해준다 
    template_name = 'product.html'
    # context_object_name = 'product_list' # 이걸 따로 지정안하면 product.html 파일에서 object_list라고 쓰면 데이터가 웹에서 보였는 데 object_list라는 명칭이 싫을 때 바꾸는 기능

@method_decorator(admin_required, name='dispatch')
class ProductCreate(FormView):
    template_name = 'register_product.html'
    form_class = RegisterForm
    success_url = '/product/' 

    def form_valid(self,form):
        product = Product(
            name=form.data.get('name'),
            price=form.data.get('price'),
            description=form.data.get('description'),
            stock=form.data.get('stock')
        )
        product.save()
        return super().form_valid(form)


class ProductDetail(DetailView):
    queryset = Product.objects.all() # 디테일뷰는 쿼리문을 이용해서 모든 제품들 중에서 하나씩 꺼내서 사용할 것임. 그래서 일단 다 꺼내놓은 것
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs): # 자세히보기 페이지에서 주문하기 기능을 위해선 해당 폼을 가져와야하는데 이 함수를 통해서 그 기능을 구현한다.
        context = super().get_context_data(**kwargs) # 디테일 뷰에 있는 데이터를 먼저 만들고나서 내가 만들고자 하는 것을 추가하는 것
        context['form'] = OrderForm(self.request) # orderform은 오더폴더에서 가져온 registerform을 앨리아스 한 것이고 뷰클래스에는 셀프안에 리퀘스트가 있다. 그래서 그냥 적어넣으면 됨
                                                  # 그러면 저 리퀘스트를 통해 order폴더 안에 있는 registerform의 리퀘스트와 연동됨. 
        return context
        