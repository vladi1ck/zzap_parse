import json

from django.contrib import admin, messages
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect
from zzap_car.tasks import search_part_numbers_process
from zzap_car.models import BrandCar, ModelCar, Car
from zzap_car.utils import fetch_car_brands
from django.urls import path
from django.core.serializers import serialize

from zzap_core.models import Search


@admin.register(BrandCar)
class BrandCarAdmin(admin.ModelAdmin):
    list_display = ('brand_car', 'brand_id', )
    actions = ['search_by_brands']

    def search_by_brands(self, request, queryset=None):
        """Метод для обновления данных о брендах автомобилей."""
        search = Search.objects.all()
        if queryset is None or len(queryset)>1:
            self.message_user(request, f"Ошибка: Выберите 1 марку", messages.ERROR)
            return
        try:
            brand_data = list(queryset.values('brand_id', 'brand_car'))
            search_part_numbers_process.delay(json.dumps(brand_data, cls=DjangoJSONEncoder))
            self.message_user(request, f"Процесс начался, примерное время ожидания - {len(search) * 30} секунд", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    search_by_brands.short_description = "Искать по выбранной марке"



    def changelist_view(self, request, extra_context=None):
        """Добавить кнопку в object-tools-items."""
        extra_context = extra_context or {}
        extra_context['show_custom_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-brands/', self.fetch_brands_view, name='fetch_brands'),
        ]
        return custom_urls + urls

    def fetch_brands_view(self, request):
        """Обработчик кнопки для обновления брендов автомобилей."""
        try:
            fetch_car_brands()
            self.message_user(request, "Данные о брендах автомобилей успешно обновлены.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

        return redirect(request.META.get('HTTP_REFERER'))


@admin.register(ModelCar)
class ModelCarAdmin(admin.ModelAdmin):
    list_display = ('model_car', 'model_id','brand', )


@admin.register(Car)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('brand_car', 'model_car', )
