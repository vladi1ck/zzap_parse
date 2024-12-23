import json
import logging
from zzap_car.utils import fetch_part_numbers_by_brands
from celery import shared_task


@shared_task
def search_part_numbers_process(brand_json):
    try:

        brand_data = json.loads(brand_json)
        for brand in brand_data:
            brand_id = brand['brand_id']
            brand_name = brand['brand_car']
            try:
                fetch_part_numbers_by_brands(brand_id, brand_name)
            except Exception as _ex:
                print(_ex)
        return "Поиск завершен успешно"
    except Exception as _ex:
        logging.error(f"Ошибка в Celery-задаче: {_ex}")
        raise
