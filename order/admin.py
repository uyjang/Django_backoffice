from django.contrib import admin
from .models import Order
from fcuser.models import Fcuser
from django.utils.html import format_html # 장고에서는 html태그를 이용해서(ex.<b>status</b>) 값을 입력하면 <b>status</b>이게 그대로 출력됨. 즉 자동으로 이스케이프를 적용시켜 놨음. 그 이스케이프 기능을 막기 위해서 사용하는 것 
from django.db.models import Q
from django.db import transaction
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse
from django.urls import path
import datetime

# Register your models here.
def refund(modelAdmin, request, queryset): # 쿼리셋은 Order.objects.filter() 이걸 이미 진행해서 데이터를 가져왔다는 뜻이고 주문목록에 있는 것들 중에서 체크박스에 체크한 것만 가져온다는 뜻
    with transaction.atomic():
        qs = queryset.filter(~Q(status='환불')) # 쿼리셋은 이미 내가 지정한 필터? 비슷한것을 통해 걸러진 데이터 인데 필터를 한번 더 넣어 걸러 줄 것이다. ~Q는 not의 의미 
        ct = ContentType.objects.get_for_model(queryset.model) # 장고에서는 어떤 모델이 앞으로 생길 지 모르니 컨텐트 타입에서 새로생기는 모델이나 정보들을 관리하고 있다. 쿼리셋을 통해 지금 가져오는게 무슨 모델인지를 정해준다.    
        for obj in qs:
            obj.product.stock += obj.quantity
            obj.product.save()

# 로그를 추가하는 코드(현재 장고가 기본적으로 로그를 남기는 것은 장고에서 만들때 지정한 것들만 남기고 내가 만든 커스텀한 데이터들은 로그를 안남기고 있다.)
            LogEntry.objects.log_action(
                # 현재 인자 안에서 사용되는 변수들은 장고가 log_action을 사용할 때 넣으라고 지정한 인자들임
                user_id = request.user.id, # 현재 로그인해서 사용하고 있는 id는 장고에서 기본적으로 request안에 저장해둠
                content_type_id = ct.pk, # 모델로 구분했으니가 당연히 pk가 있음
                object_id = obj.pk, # qs(쿼리셋)에서 object들을 하나씩 꺼냈으므로 그 쿼리셋이 가지고 있던 pk값을 obj는 가지고 있을 것이다.
                object_repr = '주문 환불', # 지금 로그 액션이 갱신하려고 하는 모델?오브젝트?의 설명을 해주는 인자
                action_flag = CHANGE, # 수정,생성,삭제 등 어떠한 액션인 지를 그림으로 표시
                change_message = '주문 환불' # 그림 뿐만아니라 메시지로도 전달
            ) # 동작이 일어날때마다 로그를 남기는 함수이고 인자를 넣을 것임

        qs.update(status='환불')
        # for obj in queryset:
        #     if obj.status == '환불': 
        #         continue
        #     obj.product.stock += obj.quantity
        #     obj.product.save() 
        # queryset.update(status='환불')

refund.short_description = '환불'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('fcuser','product','styled_status', 'action') # action은 버튼이 만들어 질 곳
    list_filter = ('status',)
    change_list_template = 'admin/order_change_list.html' # admin안에서 view역할을 하는 함수이름이 changelist였음. 그 뷰랑 연결 될 템플릿임 / 값은 템플릿이 있는 곳의 url
    change_form_template = 'admin/order_change_form.html'
    actions = [ # 액션이라는 박스를 만들고 그 안에 각각의 기능이 담긴 함수들을 넣어준다.
        refund
    ]
            

    def action(self, obj):
        if obj.status != '환불':
            return format_html(f'<input type="button" value="환불" onclick="order_refund_submit({ obj.id })" class="btn btn-primary btn-sm">') # 환불 버튼을 눌렀을 때 해당 주문정보의 id값을 가져옴


    def styled_status(self, obj):
        if obj.status == '환불':
            return format_html(f'<span style="color:red">{obj.status}</span>') # obj는 objects인데 각 오브젝트들이 갖고 있던 status반환해줌
        if obj.status == '결제완료':
            return format_html(f'<span style="color:blue">{obj.status}</span>') # obj는 objects인데 각 오브젝트들이 갖고 있던 status반환해줌
        return obj.status

    styled_status.short_description = '상태'

    # 밑에 함수들은 장고 기초에 views.py에 있었던 def order_view(): 라는 함수와 같은거임. 그냥 admins.py 파일 안에서 구분없이 사용중인 것. 즉 view의 역할을 하는 것임    
    def changelist_view(self, request, extra_context=None):# 만들어져있는 함수를 내가 만든 인자나 정보를 넣어서 오버라이딩 할 것임 / 사용자목록을 눌렀을 때 상단에 보이는 내용을 바꾸는 함수
        extra_context = { 'title' : '주문 목록'} # 템플릿에다가 전달하는 기능을 가지고 있음 
        
        if request.method == 'POST': # 버튼을 누른다면 그것은 포스트 요청인 것이고 view가 기능을 담당했던 것처럼 여기가 admin에서는 view이므로 여기에 코드 작성 
            obj_id = request.POST.get('obj_id') # 위에서 actions[]를 통해 환불로 바꿀 경우 obj_id가 없을 수도 있으므로 따로 변수를 설정
            if obj_id:
                qs = Order.objects.filter(pk=obj_id)
                ct = ContentType.objects.get_for_model(qs.model) # 장고에서는 어떤 모델이 앞으로 생길 지 모르니 컨텐트 타입에서 새로생기는 모델이나 정보들을 관리하고 있다. 쿼리셋을 통해 지금 가져오는게 무슨 모델인지를 정해준다.    
                for obj in qs:
                    obj.product.stock += obj.quantity
                    obj.product.save()

    # 로그를 추가하는 코드(현재 장고가 기본적으로 로그를 남기는 것은 장고에서 만들때 지정한 것들만 남기고 내가 만든 커스텀한 데이터들은 로그를 안남기고 있다.)
                    LogEntry.objects.log_action(
                    # 현재 인자 안에서 사용되는 변수들은 장고가 log_action을 사용할 때 넣으라고 지정한 인자들임
                        user_id = request.user.id, # 현재 로그인해서 사용하고 있는 id는 장고에서 기본적으로 request안에 저장해둠
                        content_type_id = ct.pk, # 모델로 구분했으니가 당연히 pk가 있음
                        object_id = obj.pk, # qs(쿼리셋)에서 object들을 하나씩 꺼냈으므로 그 쿼리셋이 가지고 있던 pk값을 obj는 가지고 있을 것이다.
                        object_repr = '주문 환불', # 지금 로그 액션이 갱신하려고 하는 모델?오브젝트?의 설명을 해주는 인자
                        action_flag = CHANGE, # 수정,생성,삭제 등 어떠한 액션인 지를 그림으로 표시
                        change_message = '주문 환불' # 그림 뿐만아니라 메시지로도 전달
                    ) # 동작이 일어날때마다 로그를 남기는 함수이고 인자를 넣을 것임
                qs.update(status='환불')
        return super().changelist_view(request, extra_context) # 오버라이딩을 해서 데이터를 가지게 된 원래 있던 함수를 무조건 호출해줘야됨


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None): # 사용자 목록에서 사용자를 눌러서 자세히보는 페이지 상단에 있는 제목 바꾸는 것
        order = Order.objects.get(pk=object_id)
        extra_context = { 'title' : f"'{ order.fcuser.email }'의 '{ order.product.name }' 주문 수정하기"} # 오더모델에서 fcuser랑 product는 포린키로 설정됨. 포린키 설정된 항목을 가져오는 방법
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)


    def date_view(self,request):
        week_date = datetime.datetime.now() - datetime.timedelta(days=7)
        week_data = Order.objects.filter(register_date__gte=week_date)
        data = Order.objects.filter(register_date__lt=week_date)
        context = dict(
            self.admin_site.each_context(request), # 새로만든 date_view라는 view에는 기본적으로 뭔가 넣어주는 (extra_context)같은 것들이 없다.장고 어드민에서 만들어 놓은 기본적으로 전달하는 context함수를 사용한다. 그러면 아까 site헤더나 그런 거 수정할 때 site에 반영됐던 정보값들이 들어가짐.
            week_data=week_data,
            data=data,
        )
        return TemplateResponse(request, 'admin/order_date_view.html', context)


    def get_urls(self): # 장고에서 만들어 놓은 뷰와 템플릿을 연결 시킬 때 사용하는 url함수
        urls = super().get_urls()
        date_urls = [
            path('date_view/', self.date_view),
        ]
        return date_urls + urls

    
admin.site.register(Order,OrderAdmin)