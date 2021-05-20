import json

import aiohttp
from aiohttp.typedefs import LooseHeaders

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ADS_TOKEN = os.environ.get("ADS_TOKEN")
ADATA_TOKEN = os.environ.get("ADATA_TOKEN")

MAIL = 'Tomas-Cooper@mail.ru'

API_URL = 'https://ads-api.ru/main/api'
AUTHORIZED_API_URL = f'{API_URL}?user={MAIL}&token={ADS_TOKEN}&param[2313]'

DISTRICT_API_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address?'


def set_values(url, **kwargs):
    for k, v in kwargs.items():
        if k == 'city_name':
            url += f'&q={v}'
        else:
            url += f'&{k}={v}'
    return url


async def make_request(data):
    request_url = set_values(AUTHORIZED_API_URL, category_id=2, nedvigimost_type=2, **data.dict())
    print(request_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, verify_ssl=False) as response:
            text = await response.text()

            return json.loads(text).get('data')


async def get_district(lat, lng):
    # token = "51a63a5829075787c1a7079fa79e4a3a0ce2f2a9"
    # dadata = Dadata(token)
    # # result = dadata.suggest("address", "Ленинский пр-т, 117к1")
    # result = dadata.geolocate(name="address", count=1, lat=59.851358, lon=30.252923)
    # print(result[0].get('data').get('city_district'))

    request_url = set_values(DISTRICT_API_URL, lat=lat, lon=lng, count=1)
    print(request_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(request_url, headers={
            "Accept": "application/json",
            "Authorization": f"Token {ADATA_TOKEN}"
        }, verify_ssl=False) as response:
            text = await response.text()
            print(text)

            return json.loads(text).get('suggestions')[0].get('data').get('city_district')


