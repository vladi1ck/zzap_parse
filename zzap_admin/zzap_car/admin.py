import json

from django.contrib import admin, messages
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render
from zzap_car.tasks import search_part_numbers_process, fetch_part_numbers_by_brands_process, \
    fetch_parts_count_by_part_numbers_process
from zzap_car.models import BrandCar, ModelCar, Car
from zzap_car.utils import fetch_car_brands
from django.urls import path
from django.core.serializers import serialize

from zzap_core.models import Search, PartNumbersSearchResults, Timeouts


@admin.register(BrandCar)
class BrandCarAdmin(admin.ModelAdmin):
    list_display = ('brand_car', 'brand_id', )
    actions = ['search_by_brands_only_parts', 'search_by_brands', 'search_by_brands_only_count']

    def search_by_brands(self, request, queryset=None):
        """Метод для обновления данных о брендах автомобилей."""
        search = Search.objects.all()
        timeout = Timeouts.objects.last()
        timeout_result = timeout.timeout_result
        timeout_suggest = timeout.timeout_suggest

        if queryset is None or len(queryset)>1:
            self.message_user(request, f"Ошибка: Выберите 1 марку", messages.ERROR)
            return
        try:
            brand_data = list(queryset.values('brand_id', 'brand_car'))
            brand_car = brand_data[0]['brand_car']
            brand_id = brand_data[0]['brand_id']
            result_1 = fetch_part_numbers_by_brands_process.delay(brand_id, brand_car)
            self.message_user(request, f"Процесс начался, примерное время ожидания - {((len(search) * timeout_suggest) + (50 * timeout_result))/60} минут", messages.SUCCESS)
            result_1.get()
            search_data = Search.objects.all()
            for search in search_data:
                search_part_numbers = (PartNumbersSearchResults.objects.filter(search_id=search.id).order_by().
                                       values('part_number').distinct())

                for part in search_part_numbers:
                    print(part)
                    task_1 = fetch_parts_count_by_part_numbers_process.delay(brand_car, part, search.id)
                    task_1.get()
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    search_by_brands.short_description = "Искать по выбранной марке (heavy)"

    def search_by_brands_only_count(self, request, queryset=None):
        """Метод для обновления данных о брендах автомобилей."""
        search = Search.objects.all()
        timeout = Timeouts.objects.last()
        timeout_result = timeout.timeout_result
        timeout_suggest = timeout.timeout_suggest

        if queryset is None or len(queryset)>1:
            self.message_user(request, f"Ошибка: Выберите 1 марку", messages.ERROR)
            return
        try:
            brand_data = list(queryset.values('brand_id', 'brand_car'))
            brand_car = brand_data[0]['brand_car']
            search_data = Search.objects.all()
            parts = PartNumbersSearchResults.objects.filter(brand_car=brand_car)
            self.message_user(request,
                              f"Процесс начался, примерное время ожидания - {(len(parts) * timeout_result) / 60} минут",
                              messages.SUCCESS)
            for search in search_data:
                i = 0
                search_part_numbers = (PartNumbersSearchResults.objects.filter(search_id=search.id).order_by().
                                       values('part_number').distinct())

                for part in search_part_numbers:
                    task_1 = fetch_parts_count_by_part_numbers_process.delay(brand_car, part['part_number'], search.id)
                    task_1.get()

        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    search_by_brands_only_count.short_description = "Искать по выбранной марке (light)"

    def search_by_brands_only_parts(self, request, queryset=None):
        """Метод для обновления данных о брендах автомобилей."""
        search = Search.objects.all()
        timeout = Timeouts.objects.last()
        timeout_result = timeout.timeout_result
        timeout_suggest = timeout.timeout_suggest

        if queryset is None or len(queryset)>1:
            self.message_user(request, f"Ошибка: Выберите 1 марку", messages.ERROR)
            return
        try:
            brand_data = list(queryset.values('brand_id', 'brand_car'))
            brand_car = brand_data[0]['brand_car']
            brand_id = brand_data[0]['brand_id']
            fetch_part_numbers_by_brands_process.delay(brand_id, brand_car)
            self.message_user(request,
                              f"Процесс начался, примерное время ожидания - {(len(search) * timeout_suggest) / 60} минут",
                              messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    search_by_brands_only_parts.short_description = "Искать только артикулы"


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
