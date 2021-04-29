from django import forms
from .models import Product

class RegisterForm(forms.Form):
    name = forms.CharField(
        error_messages={'required': '상품명을 입력해주세요.'}, max_length=128, label='상품명' # 폼에서는 라벨, 모델에서는 verbose_name
    )
    price = forms.IntegerField(
        error_messages={'required': '상품가격을 입력해주세요.'}, label='상품가격'
    )
    description = forms.CharField(
        error_messages={'required': '상품설명을 입력해주세요'}, label='상품설명'
    )
    stock = forms.IntegerField(
        error_messages={'required': '재고를 입력해주세요'}, label='재고'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        name = self.cleaned_data.get('name')
        price = self.cleaned_data.get('price')
        description = self.cleaned_data.get('description')
        stock = self.cleaned_data.get('stock')

        if not (name and price and description and stock):
            self.add_error('name', '상품명값이 없습니다.')
            self.add_error('price', '가격값이 없습니다.')
            self.add_error('description', '상품설명값이 없습니다.')
            self.add_error('stock', '재고값이 없습니다.')


                
    
    
