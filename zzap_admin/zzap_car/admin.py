from django.contrib import admin, messages
from django.shortcuts import redirect

from zzap_car.models import BrandCar, ModelCar, Car
from zzap_car.utils import fetch_car_brands
from django.urls import path


@admin.register(BrandCar)
class BrandCarAdmin(admin.ModelAdmin):
    list_display = ('brand_car', 'brand_id', )

    # Определим действия, которые можно выполнить
    def fetch_brands(self, request, queryset=None):
        """Метод для обновления данных о брендах автомобилей."""
        try:
            fetch_car_brands()  # Например, ваш метод для обновления данных
            self.message_user(request, "Данные о брендах автомобилей успешно обновлены.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    fetch_brands.short_description = "Обновить данные о брендах автомобилей"

    def changelist_view(self, request, extra_context=None):
        """Добавить кнопку в object-tools-items."""
        extra_context = extra_context or {}
        extra_context['show_custom_button'] = True  # Устанавливаем флаг для кнопки
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
            fetch_car_brands()  # Ваш код для получения данных о брендах
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
