# 시리얼라이저는 form이랑 하는 기능이 똑같다고 보면됨. 유효성검사하고 데이터 베이스에 저장하고 등등
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'