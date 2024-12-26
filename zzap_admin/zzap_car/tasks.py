import json
import logging
import os
import time
import requests
from zzap_car.models import BrandCar
from zzap_car.utils import  from_xml_to_json
from celery import shared_task

from zzap_core.models import Search, Timeouts, PartNumbersSearchResults, PartNumbersCount, SinglePartNumbers

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

# error = '[100]:Превышена максимальная частота запросов..'
count_part = 0
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@shared_task
def search_part_numbers_process(brand_json):
    try:
        brand_data = json.loads(brand_json)
        for brand in brand_data:
            brand_id = brand['brand_id']
            brand_name = brand['brand_car']
            try:
                progress = fetch_part_numbers_by_brands_process(brand_id, brand_name)
            except Exception as _ex:
                print(_ex)
        return progress
    except Exception as _ex:
        logging.error(f"Ошибка в Celery-задаче: {_ex}")
        raise



@shared_task
def fetch_part_numbers_by_brands_process(brand_id, brand_name):
    """Отправка запроса и сохранение артикулов запчастей автомобилей"""
    global count_part
    url = f'{MAIN_URL}/{GET_SUGGEST}'
    search_data = Search.objects.all()
    timeout = Timeouts.objects.last()
    timeout_result = timeout.timeout_result
    timeout_suggest = timeout.timeout_suggest
    count = 0

    try:
        for search in search_data:
            print(search.search_string)
            payload['search_text'] = f'{search.search_string} {brand_name}'
            payload['row_count'] = 1000
            payload['type_request'] = 4
            payload['class_man'] = brand_name
            response = requests.post(url, payload)
            part_numbers_json = from_xml_to_json(response.text)
            try:
                print(part_numbers_json['terms'])
                error = part_numbers_json['error']
                row_count = part_numbers_json['row_count']
                print(row_count)
                for part_number in part_numbers_json['table']:
                    if part_number['partnumber'] is None:
                        break
                    if not PartNumbersSearchResults.objects.filter(
                            brand_car=BrandCar.objects.get(brand_car=brand_name),
                            search_id=Search.objects.get(id=search.id),
                            part_number=part_number['partnumber']
                    ).exists():
                        PartNumbersSearchResults.objects.get_or_create(
                            brand_car=BrandCar.objects.get(brand_car=brand_name),
                            part_number=part_number['partnumber'],
                            defaults={
                                'search_id' : Search.objects.get(id=search.id),
                                'class_cat': part_number['class_cat'],
                            }
                        )

                        count +=1
                print(count)
            except Exception as _ex:
                print(f"Ошибка запроса: {error}")
                print(_ex)
            finally:
                time.sleep(timeout_suggest)
    except Exception as _ex:
        logging.debug(_ex)
    finally:
        count_part = 0
        time.sleep(timeout_suggest)


@shared_task
def fetch_parts_count_by_part_numbers_process(brand_name, part_number, search_id:None):
    """Отправка запроса и сохранение артикулов запчастей автомобилей"""
    global count_part
    timeout = Timeouts.objects.last()
    timeout_result = timeout.timeout_result
    timeout_suggest = timeout.timeout_suggest
    url = f'{MAIN_URL}/{GET_RESULTS_LIGHT}'
    if PartNumbersSearchResults.objects.filter(part_number=part_number).exists():
        name = PartNumbersSearchResults.objects.filter(part_number=part_number).last()
        search_id = name.search_id.id
    else:
        name = SinglePartNumbers.objects.filter(part_number=part_number).last()
    class_cat = name.class_cat
    if search_id is None:
        search_id = Search.objects.get(search_string='').id
    try:

        payload['row_count'] = 1000
        payload['search_text'] = ''
        payload['type_request'] = 4
        payload['class_man'] = brand_name
        payload['partnumber'] = part_number
        payload['code_region'] = 1

        response = requests.post(url, payload)
        part_numbers_json = from_xml_to_json(response.text)
        print(part_numbers_json)
        error = part_numbers_json['error']
        try:
            PartNumbersCount.objects.create(
                brand_car=BrandCar.objects.get(brand_car=brand_name),
                search_id=Search.objects.get(id=search_id),
                class_cat=class_cat,
                part_number=part_numbers_json['partnumber'],
                count=part_numbers_json['price_count_instock']
            )
            count_part +=1
            print(count_part)
        except Exception as _ex:
            print(_ex)
            print(f"Ошибка запроса: {error}")
            time.sleep(timeout_result)
        finally:
            time.sleep(timeout_result)
    except Exception as _ex:
        logging.debug(_ex)

