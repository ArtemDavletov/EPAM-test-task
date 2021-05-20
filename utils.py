import json

from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(self, o)


def count_psm(flat: dict):
    return float(flat['price']) / float(flat['params']['Площадь'])