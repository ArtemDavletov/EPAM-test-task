from fastapi import APIRouter
from pymongo import MongoClient
from geojson import Point, utils

from lib import make_request, get_district
from mongo import get_collection, get_district_average_psm_mapping
from schema import ParseCityRequest, FlatDBEntity, PositionCityResponse
from utils import JSONEncoder, count_psm

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
            response.append(collection.insert(FlatDBEntity(**flat, psm=count_psm(flat), district=district).dict()))

    return JSONEncoder().encode(response)


@router.get(
    "/positions/{city_name}"
)
async def positions(
        city_name: str
):
    collection = get_collection(client=client, collection_name=city_name)
    result = collection.find({"city1": city_name}, {"coords": 1, "address": 1, "psm": 1, "district": 1})

    # response = [PositionCityResponse(**_) for _ in result]
    # for _ in result:
    #     district = await get_district(**_.get('coords'))
    #     if district is not None:
    #         response.append(PositionCityResponse(**_, district=district))

    return [PositionCityResponse(**_) for _ in result]


@router.get(
    "/geojson"
)
async def get_geojson(
    city_name: str
):
    collection = get_collection(client=client, collection_name=city_name)
    result = collection.find({"city1": city_name}, {"coords": 1, "address": 1, "psm": 1, "district": 1})

    for r in result:
        point = Point(r["coords"])


    points = geojson.utils.map_geometries(geojson.GeometryCollection([lambda g: geojson.Point([g["coords"]]), geojson.Point(result)]))
    return points


@router.get(
    "/average_psm"
)
async def get_average_psm(
    city_name: str
):
    collection = get_collection(client=client, collection_name=city_name)
    result = get_district_average_psm_mapping(collection)
    return result