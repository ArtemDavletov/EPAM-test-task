import json

import aiohttp
from aiohttp.typedefs import LooseHeaders

import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

import os
from os.path import join, dirname
from dotenv import load_dotenv

import shortuuid

# TODO: Put it all to settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ADS_TOKEN = os.environ.get("ADS_TOKEN")
ADATA_TOKEN = os.environ.get("ADATA_TOKEN")

MAIL = 'Tomas-Cooper@mail.ru'

API_URL = 'https://ads-api.ru/main/api'
AUTHORIZED_API_URL = f'{API_URL}?user={MAIL}&token={ADS_TOKEN}&param[2313]'

DISTRICT_API_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address?'

Y_LABEL_MAPPING = {
    "psm": "Цена за квадратный метр (руб/кв.метр)",
    "area": "Метраж (кв метров)"
}


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


def create_hist(data, city_name:str, field_name: str):
    hist_path = f'tmp/{shortuuid.uuid()}.png'  # sttings.TMP_PATH / "{shortuuid.uuid()}.png"

    plt.figure(figsize=(10,10))
    plt.bar(list(data.keys()), data.values(), color='#607c8e')

    plt.title(f'Цена съема жилья на квадратный метр в городе {city_name}')
    plt.xlabel('Районы')
    
    plt.ylabel(Y_LABEL_MAPPING[field_name])

    plt.tick_params(axis='x', rotation=40)
    plt.tight_layout()
    
    plt.savefig(hist_path)
    return hist_path