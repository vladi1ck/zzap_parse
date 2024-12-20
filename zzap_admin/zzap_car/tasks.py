import json
import logging
import time

from zzap_car.utils import fetch_part_numbers_by_brands
from celery import shared_task


@shared_task
def search_part_numbers_process(brand_json):
    try:
        brand_data = json.loads(brand_json)
        for brand in brand_data:
            brand_id = brand['brand_id']
            brand_name = brand['brand_car']
            fetch_part_numbers_by_brands(brand_id, brand_name)
        return "Поиск завершен успешно"
    except Exception as _ex:
        logging.error(f"Ошибка в Celery-задаче: {_ex}")
        raise
