import json
import os
import xml.etree.ElementTree as ET
import dotenv
import requests
from zzap_car.models import BrandCar

dotenv.load_dotenv()

API_KEY = os.getenv('api_key')
MAIN_URL = os.getenv('MAIN_URL')
GET_BRANDS = os.getenv('GET_BRANDS')

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