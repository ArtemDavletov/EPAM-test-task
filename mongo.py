from pymongo import MongoClient


def get_db(client: MongoClient):
    return client['ads']  # setting.DB_NAME


def get_collection(client: MongoClient, collection_name: str):
    db = get_db(client)
    return db[collection_name]


def get_all_districts(collection):
    return collection.distinct('district')


def get_district_average_psm_mapping(collection):
    district_average_psm_map = dict()

    cursor = collection.aggregate([{'$group': {'_id': {'district': '$district'}, 'psm_avg': {'$avg': '$psm'}}}])
    
    for cur in cursor:
        print(cur)
        district_average_psm_map[cur['_id']['district']] = cur['psm_avg']
    
    return district_average_psm_map

    

