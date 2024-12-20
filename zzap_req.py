import json
import os
import xml.etree.ElementTree as ET
import dotenv
import requests


"""
Поиск всех предложений и поиск только новых деталей осуществляется по артикулу детали, 
а поиск б/у, восстановленных, неликвидных и прочих уценённых запчастей можно проводить как по номеру, 
так и по наименованию

type_request: 
            0 - поиск любых запчастей по номеру, 
            1 - поиск только новых запчастей по номеру, 
            2 - поиск по б/у и уценке (по введённым в поисковую строку словам)
            4 - любые только по запрошенному номеру, 
            5 - только новые и только по запрошенному номеру
"""

dotenv.load_dotenv()

payload = {
        "login":"",
        "password":"",
        "search_text":"",
        "row_count":"100000",
        "type_request":"5",
        "partnumber":"",
        "class_man":"",
        "code_region":"1",
        "api_key":""
    }

code_doc_b = 497632882570027184
part_number = "17117652234"
code_region = "1"
class_man = "BMW"
api_key = os.getenv('api_key', None)
search_text = 'Фара BMW'
# search_text = ''
payload['api_key'] = api_key
payload['search_text'] = search_text
payload['partnumber'] = part_number
payload['code_region'] = code_region
payload['class_man'] = class_man
payload['code_doc_b'] = code_doc_b

url = "https://api.zzap.pro/webservice/datasharing.asmx/GetSearchSuggestV3"
url_search_light = "https://api.zzap.pro/webservice/datasharing.asmx/GetSearchResultV3"
url_search_one = "https://api.zzap.pro/webservice/datasharing.asmx/GetSearchResultOne"


def from_xml_to_json(xml_text):
    root = ET.fromstring(xml_text)
    json_string = root.text
    json_data = json.loads(json_string)

    return json.dumps(json_data, indent=10, ensure_ascii=False)

if __name__ == '__main__':
    response = requests.post(url=url, data=payload)

    if response.status_code == 200:
        json_answer = from_xml_to_json(response.text)
        print(json_answer)
    else:
        print('Error')
