from django.contrib import admin
from .models import Fcuser
# Register your models here.

class FcuserAdmin(admin.ModelAdmin): # modeladmin안에는 changelist_view라는 함수가 이미 만들어져있음
    list_display = ('email',)

    def changelist_view(self, request, extra_context=None):# 만들어져있는 함수를 내가 만든 인자나 정보를 넣어서 오버라이딩 할 것임 / 사용자목록을 눌렀을 때 상단에 보이는 내용을 바꾸는 함수
        extra_context = { 'title' : '사용자 목록'} # 템플릿에다가 전달하는 기능을 가지고 있음 
        return super().changelist_view(request, extra_context) # 오버라이딩을 해서 데이터를 가지게 된 원래 있던 함수를 무조건 호출해줘야됨

    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None): # 사용자 목록에서 사용자를 눌러서 자세히보는 페이지 상단에 있는 제목 바꾸는 것
        fcuser = Fcuser.objects.get(pk=object_id)
        extra_context = { 'title' : f'{ fcuser.email} 수정하기'}
        return super().changeform_view(request, object_id, form_url, extra_context)


admin.site.register(Fcuser, FcuserAdmin)