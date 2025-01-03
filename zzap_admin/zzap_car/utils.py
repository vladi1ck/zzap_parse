import json
import logging
import os
import time
import xml.etree.ElementTree as ET
import dotenv
import requests
from zzap_car.models import BrandCar


dotenv.load_dotenv()

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

count_part = 0

def from_xml_to_json(xml_text):
    root = ET.fromstring(xml_text)
    json_string = root.text
    json_data = json.loads(json_string)

    return json_data

def fetch_car_brands():
    """Отправка запроса и сохранение данных о брендах автомобилей"""
    url = f'{MAIN_URL}/{GET_BRANDS}'
    response = requests.post(url, payload)

    if response.status_code == 200:
        brands = response.text
        brands_json = from_xml_to_json(brands)

        for brand in brands_json['table']:
            BrandCar.objects.update_or_create(
                brand_id=brand['code_man'],
                defaults={'brand_car': brand['class_man']}
            )
    else:
        raise Exception(f"Ошибка запроса: {response.status_code}")

#
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#
#
# def fetch_part_numbers_by_brands(brand_id, brand_name):
#     """Отправка запроса и сохранение артикулов запчастей автомобилей"""
#     global count_part
#     url = f'{MAIN_URL}/{GET_SUGGEST}'
#     search_data = Search.objects.all()
#     timeout = Timeouts.objects.last()
#     timeout_result = timeout.timeout_result
#     timeout_suggest = timeout.timeout_suggest
#     count = 0
#
#     try:
#         for search in search_data:
#             print(search.search_string)
#             payload['search_text'] = f'{search.search_string} {brand_name}'
#             payload['row_count'] = 1000
#             payload['type_request'] = 4
#             payload['class_man'] = brand_name
#             response = requests.post(url, payload)
#             if response.status_code == 200:
#                 part_numbers_json = from_xml_to_json(response.text)
#                 row_count = part_numbers_json['row_count']
#                 print(part_numbers_json['table'])
#
#                 for part_number in part_numbers_json['table']:
#                     if part_number['partnumber'] is None:
#                         break
#                     if not PartNumbersSearchResults.objects.filter(
#                             brand_id=BrandCar.objects.get(brand_id=brand_id),
#                             search_id=Search.objects.get(id=search.id),
#                             part_number=part_number['partnumber']
#                     ).exists():
#                         PartNumbersSearchResults.objects.get_or_create(
#                             brand_id=BrandCar.objects.get(brand_id=brand_id),
#                             part_number=part_number['partnumber'],
#                             defaults={
#                                 'search_id' : Search.objects.get(id=search.id),
#                                 'class_cat': part_number['class_cat'],
#                             }
#                         )
#
#                         count +=1
#                     time.sleep(timeout_result)
#                     progress = fetch_parts_count_by_part_numbers(brand_id, brand_name, part_number['partnumber'], search.id, row_count)
#                 print(count)
#
#
#             else:
#                 raise Exception(f"Ошибка запроса: {response.status_code}")
#             time.sleep(timeout_suggest)
#             return progress
#     except Exception as _ex:
#         logging.debug(_ex)
#     finally:
#         count_part = 0
#
# def fetch_parts_count_by_part_numbers(brand_id ,brand_name, part_number, search_id, row_count):
#     """Отправка запроса и сохранение артикулов запчастей автомобилей"""
#     global count_part
#     timeout = Timeouts.objects.last()
#     timeout_result = timeout.timeout_result
#     timeout_suggest = timeout.timeout_suggest
#     url = f'{MAIN_URL}/{GET_RESULTS_LIGHT}'
#     try:
#
#         payload['row_count'] = 1000
#         payload['search_text'] = ''
#         payload['type_request'] = 4
#         payload['class_man'] = brand_name
#         payload['partnumber'] = part_number
#         payload['code_region'] = 1
#         if count_part == 0:
#             time.sleep(timeout_result)
#         response = requests.post(url, payload)
#
#         if response.status_code == 200:
#             part_numbers_json = from_xml_to_json(response.text)
#             error = '[100]: Превышена максимальная частота запросов..'
#             try:
#                 if error in part_numbers_json['error']:
#                     time.sleep(timeout_result+3)
#                     print(part_numbers_json['error'])
#                 else:
#                     PartNumbersCount.objects.create(
#                         brand_id=BrandCar.objects.get(brand_id=brand_id),
#                         search_id=Search.objects.get(id=search_id),
#                         part_number=part_numbers_json['partnumber'],
#                         count=part_numbers_json['price_count_instock'],
#                     )
#                     count_part +=1
#                     progress_message = f'{count_part}/{row_count}'
#                     print(progress_message)  # Для логов
#                     return progress_message
#             except Exception as _ex:
#                 print(_ex)
#         else:
#             raise Exception(f"Ошибка запроса: {response.status_code}")
#     except Exception as _ex:
#         logging.debug(_ex)
