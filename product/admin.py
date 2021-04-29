from django.contrib import admin
from .models import Product
from django.utils.html import format_html # 장고에서는 html태그를 이용해서(ex.<b>status</b>) 값을 입력하면 <b>status</b>이게 그대로 출력됨. 즉 자동으로 이스케이프를 적용시켜 놨음. 그 이스케이프 기능을 막기 위해서 사용하는 것 
from django.contrib.humanize.templatetags.humanize import intcomma # 함수처럼 사용하고 싶다면 휴머나이즈 밑에 템플릿태그 밑에 있는 휴머나이즈를 가져오면 됨
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','styled_price', 'styled_stock')


    def styled_stock(self, obj):
        stock = obj.stock
        if stock <= 10:
            stock = intcomma(stock)
            return format_html(f'<b><span style="color:red">{stock} 개</span></b>') # obj는 objects인데 각 오브젝트들이 갖고 있던 status반환해줌
        # if obj.status == '결제완료':
        #     return format_html(f'<span style="color:blue">{obj.status}</span>') # obj는 objects인데 각 오브젝트들이 갖고 있던 status반환해줌
        return f'{intcomma(stock)} 개' 

    styled_stock.short_description = '재고'


    def styled_price(self, obj):
        price = intcomma(obj.price)
        return f'{price} 원'

    styled_price.short_description = '가격'


    def changelist_view(self, request, extra_context=None):# 만들어져있는 함수를 내가 만든 인자나 정보를 넣어서 오버라이딩 할 것임 / 사용자목록을 눌렀을 때 상단에 보이는 내용을 바꾸는 함수
        extra_context = { 'title' : '상품 목록'} # 템플릿에다가 전달하는 기능을 가지고 있음 
        return super().changelist_view(request, extra_context) # 오버라이딩을 해서 데이터를 가지게 된 원래 있던 함수를 무조건 호출해줘야됨

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None): # 사용자 목록에서 사용자를 눌러서 자세히보는 페이지 상단에 있는 제목 바꾸는 것
        product = Product.objects.get(pk=object_id)
        extra_context = { 'title' : f'{ product.name} 수정하기'}
        return super().changeform_view(request, object_id, form_url, extra_context)


    
admin.site.register(Product,ProductAdmin)