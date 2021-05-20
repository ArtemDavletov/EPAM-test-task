from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pymongo import MongoClient
from geojson import Point, utils

import folium
from folium.plugins import HeatMap

from lib import make_request, get_district, create_hist
from mongo import get_collection, get_district_average_field_mapping, get_coords
from schema import ParseCityRequest, FlatDBEntity, PositionCityResponse
from utils import JSONEncoder, count_psm, extract_area, prepare_coords_data

router = APIRouter()
client: MongoClient = MongoClient('mongodb://localhost:27018/')


@router.get("/")
def root():
    return 'success'


@router.post(
    "/parse"
)
async def parse(
        request: ParseCityRequest
):
    data = await make_request(request)

    collection = get_collection(client=client, collection_name=request.city_name)

    response = []
    for flat in data:
        district = await get_district(**flat.get('coords'))
        
        if district is not None:
            response.append(collection.insert(FlatDBEntity(**flat, psm=count_psm(flat), district=district, area=extract_area(flat)).dict()))

    return JSONEncoder().encode(response)


@router.get(
    "/positions/{city_name}"
)
async def positions(
        city_name: str
):
    collection = get_collection(client=client, collection_name=city_name)
    result = collection.find({"city1": city_name}, {"coords": 1, "address": 1, "psm": 1, "district": 1})

    return [PositionCityResponse(**_) for _ in result]


@router.get(
    "/average/{city_name}/{field_name}"
)
async def get_average(
    city_name: str,
    field_name: str
):
    if field_name not in ("psm", "area"):
        raise HTTPException(status_code=404, detail='Field is not supported. Use one of ("psm", "area")')
    
    collection = get_collection(client=client, collection_name=city_name)
    result = get_district_average_field_mapping(collection=collection, field=field_name)
    return result


@router.get(
    "/build_hist/{city_name}/{field_name}"
)
async def build_hist(
    city_name: str,
    field_name: str
):
    if field_name not in ("psm", "area"):
        raise HTTPException(status_code=404, detail='Field is not supported. Use one of ("psm", "area")')

    collection = get_collection(client=client, collection_name=city_name)
    result = get_district_average_field_mapping(collection=collection, field=field_name)

    hist_path = create_hist(result, city_name, field_name)

    return FileResponse(hist_path)


@router.get(
    "/heatmap"
)
async def heatmap(
    city_name: str
):
    collection = get_collection(client=client, collection_name=city_name)
    result = get_coords(collection, city_name)

    coords_list = list(map(lambda flat: prepare_coords_data(flat), result))

    m = folium.Map([59.6, 30.2], tiles="stamentoner", zoom_start=6)

    HeatMap(coords_list).add_to(m)

    return HTMLResponse(m._repr_html_())
