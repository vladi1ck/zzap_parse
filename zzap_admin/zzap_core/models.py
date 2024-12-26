from django.db import models
import os
from zzap_car.models import BrandCar
import logging
import requests

from zzap_car.utils import from_xml_to_json
from zzap_req import part_number

API_KEY = os.getenv('api_key2')
MAIN_URL = os.getenv('MAIN_URL')
GET_BRANDS = os.getenv('GET_BRANDS')
GET_SUGGEST = os.getenv('GET_SUGGEST')
GET_RESULTS = os.getenv('GET_RESULTS')
GET_RESULTS_LIGHT = os.getenv('GET_RESULTS_LIGHT')


payload = {
    'login': '',
    'password': '',
    'api_key': API_KEY,
}

class Search(models.Model):
    search_string = models.TextField( blank=True)
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']

    def __str__(self):
        return self.search_string

class PartNumbersSearchResults(models.Model):
    brand_car = models.ForeignKey(BrandCar, to_field='brand_car', on_delete=models.CASCADE)
    search_id = models.ForeignKey(Search, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=255, null=False, blank=False)
    class_cat = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Результат Поиска для Артикулов'
        verbose_name_plural = 'Результаты Поиска для Артикулов'
        constraints = [
            models.UniqueConstraint(fields=['brand_car', 'part_number'], name='unique_part_per_brand')
        ]
        ordering = ['id']

    def __str__(self):
        return f"{self.part_number} ({self.brand_car})"

class PartNumbersCount(models.Model):
    brand_car = models.ForeignKey(BrandCar, to_field='brand_car', on_delete=models.CASCADE)
    search_id = models.ForeignKey(Search, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=255, null=False, blank=False)
    count = models.IntegerField(default=0)
    class_cat = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Результат Поиска Запчасти (количество)'
        verbose_name_plural = 'Результаты Поиска Запчасти (количество)'
        ordering = ['-id']

    def __str__(self):
        return f"{self.part_number} ({self.brand_car}) - {self.count}"

class Timeouts(models.Model):
    timeout_result = models.IntegerField(default=6)
    timeout_suggest = models.IntegerField(default=30)


class SinglePartNumbers(models.Model):
    brand_car = models.ForeignKey(BrandCar, to_field='brand_car', on_delete=models.CASCADE, null=True, blank=True)
    part_number = models.CharField(max_length=255, null=False, blank=False, unique=True)
    class_cat = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Артикул'
        verbose_name_plural = 'Артикулы'
        ordering = ['id']

    def __str__(self):
        return f"{self.part_number} ({self.brand_car})"

    def fetch_data_from_api(self):
        """Отправка запроса и сохранение артикулов запчастей автомобилей"""
        url = f'{MAIN_URL}/{GET_SUGGEST}'
        try:
            payload['row_count'] = 1000
            payload['search_text'] = self.part_number
            payload['type_request'] = 0
            payload['class_man'] = ''
            payload['partnumber'] = self.part_number
            payload['code_region'] = 1

            response = requests.post(url, payload)

            part_numbers_json = from_xml_to_json(response.text)
            print(part_numbers_json)
            error = part_numbers_json['error']
            try:
                for item in part_numbers_json['table']:
                    if item['partnumber'] == self.part_number:
                        self.brand_car = BrandCar.objects.get(brand_car=item['class_man'])
                        self.class_cat = item['class_cat']
            except Exception as _ex:
                print(f"Ошибка запроса: {_ex}")
        except Exception as _ex:
            logging.debug(_ex)

    def save(self, *args, **kwargs):
        if self.brand_car is None or self.class_cat is None:
            try:
                self.fetch_data_from_api()
            except Exception as ex:
                logging.error(f"Ошибка при вызове fetch_data_from_api: {ex}")
        super().save(*args, **kwargs)
