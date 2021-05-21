import json

from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(self, o)


def count_psm(flat: dict) -> float:
    return float(flat['price']) / float(flat['params']['Площадь'])


def extract_area(flat: dict) -> float:
    return float(flat['params']['Площадь'])


def prepare_coords_data(data, field: str = 'psm'):
    return [*data['coords'].values(), data[field]]
