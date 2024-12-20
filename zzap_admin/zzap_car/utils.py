import json
import logging
import os
import time
import xml.etree.ElementTree as ET
import dotenv
import requests
from zzap_car.models import BrandCar
from zzap_core.models import SearchResults, Search

dotenv.load_dotenv()

API_KEY = os.getenv('api_key')
MAIN_URL = os.getenv('MAIN_URL')
GET_BRANDS = os.getenv('GET_BRANDS')
GET_SUGGEST = os.getenv('GET_SUGGEST')

payload = {
    'login': '',
    'password': '',
    'api_key': API_KEY,
}

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

def fetch_part_numbers_by_brands(brand_id, brand_name):
    """Отправка запроса и сохранение артикулов запчастей автомобилей"""
    url = f'{MAIN_URL}/{GET_SUGGEST}'
    search_data = Search.objects.all()
    try:
        for search in search_data:
            print(search.search_string)
            payload['search_text'] = f'{search.search_string} {brand_name}'
            payload['row_count'] = 1000
            payload['type_request'] = 4
            payload['class_man'] = brand_name
            response = requests.post(url, payload)
            if response.status_code == 200:
                part_numbers_json = from_xml_to_json(response.text)
                print(part_numbers_json)

                for part_number in part_numbers_json['table']:
                    if not SearchResults.objects.filter(
                            brand_id=BrandCar.objects.get(brand_id=part_number['code_man']),
                            search_id=Search.objects.get(id=search.id),
                            part_number=part_number['partnumber'],
                            class_cat=part_number['class_cat'],
                    ).exists():
                        SearchResults.objects.get_or_create(
                            brand_id=BrandCar.objects.get(brand_id=part_number['code_man']),
                            part_number=part_number['partnumber'],
                            defaults={
                                'search_id' : Search.objects.get(id=search.id),
                                'class_cat': part_number['class_cat'],  # Установится только если создаётся новая запись
                            }
                        )
                    else:
                        continue
            else:
                raise Exception(f"Ошибка запроса: {response.status_code}")
            time.sleep(30)
    except Exception as _ex:
        logging.debug(_ex)


def fetch_parts_by_part_numbers(brand_name):
    """Отправка запроса и сохранение артикулов запчастей автомобилей"""
    url = f'{MAIN_URL}/{GET_SUGGEST}'
    search_data = Search.objects.all()
    try:
        for search in search_data:
            payload['search_text'] = f'{search.search_string} {brand_name}'
            payload['row_count'] = 1000
            payload['type_request'] = 4
            payload['class_man'] = brand_name
            response = requests.post(url, payload)
            if response.status_code == 200:
                part_numbers_json = from_xml_to_json(response.text)

                for part_number in part_numbers_json['table']:

                    SearchResults.objects.create(
                        brand_id=BrandCar.objects.get(brand_id=part_number['code_man']),
                        search_id=Search.objects.get(id=search.id),
                        part_number=part_number['partnumber'],
                        class_cat=part_number['class_cat'],
                    )
            else:
                raise Exception(f"Ошибка запроса: {response.status_code}")
            time.sleep(6)
    except Exception as _ex:
        logging.debug(_ex)