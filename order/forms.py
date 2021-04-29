from django import forms
from .models import Order
from product.models import Product
from fcuser.models import Fcuser
from django.db import transaction # 일련의 동작들이 연속적으로 완료돼야함. 예를들면 주문을하면 주문목록이 늘어나고 동시에 재고는 줄어들어야 됨

class RegisterForm(forms.Form):
    def __init__(self,request,*args, **kwargs): # forms.py에서는 리퀘스트를 현재 사용할 수가 없음(POST방식이라서). 그래서 request가 한번도 나온적이 없었음
        super().__init__(*args,**kwargs)  # 리퀘스트를 사용하기 위해 클래스가 생성될 때 생성자를 만들면서 forms가 원래 갖고 있던 이닛함수를 실행하고 거기에 리퀘스트를 집어넣음
        self.request = request

    quantity = forms.IntegerField(
        error_messages={'required': '수량을 입력해주세요.'}, label='수량'
    )
    product = forms.IntegerField(
        error_messages={'required': '상품명을 입력해주세요'}, label='상품명', widget=forms.HiddenInput # 주문하기를 누르면 내가 상품명을 입력하는 게 아니라 상품명이 알아서 끌려 오도록 해야됨(상품자세히보기 페이지에서 주문을 만들도록 설계돼있으므로)
    )
     
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        fcuser = self.request.session.get('user')

        if not (quantity and product):               
            self.add_error('quantity', '수량값이 없습니다.')
            self.add_error('product', '상품값이 없습니다.')
        

                
    
    
