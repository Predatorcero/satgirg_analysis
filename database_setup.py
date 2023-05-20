import datetime
import pymongo
import config
from pandas import DataFrame


def insert_experiment_to_db(tag: str, platform: str):
    with new_mongodb_client() as mongodb_client:
        database = mongodb_client["satgirg_experiments"]
        experiment = {"tag": tag, "experiment_time": datetime.datetime.utcnow()}
        new_record = database[platform + "_experiment"].insert_one(experiment)
        return new_record.inserted_id


def insert_datapoint(experiment_id, datapoint: dict, platform: str):
    with new_mongodb_client() as mongodb_client:
        database = mongodb_client["satgirg_experiments"]
        datapoint["experiment_id"] = experiment_id
        database[platform + "_data"].insert_one(datapoint)


def new_mongodb_client():
    uri = f'mongodb://{config.MONGODB_USERNAME}:{config.MONGODB_PASSWORD}@' \
          f'{config.MONGODB_SERVER}:{config.MONGODB_PORT}/'
    return pymongo.MongoClient(uri)


def delete_experiment_from_db(tag: str, platform: str):
    with new_mongodb_client() as mongodb_client:
        database = mongodb_client["satgirg_experiments"]
        database[platform + "_experiment"].delete_many({"tag": tag})


def experiments_for_platform(platform: str) -> DataFrame:
    with new_mongodb_client() as client:
        database = client["satgirg_experiments"]
        experiments = database[platform + "_experiment"].find()
        experiments_df = DataFrame(experiments)
        return experiments_df


def data_from_experiment(experiment_id, platform: str) -> DataFrame:
    with new_mongodb_client() as mongodb_client:
        database = mongodb_client["satgirg_experiments"]
        data = database[platform + "_data"]
        return DataFrame(data.find({"experiment_id": experiment_id}))