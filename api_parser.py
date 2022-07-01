import logging
import os
import time

import requests
from celery import Celery
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)


def mongodb_connection():
    client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://root:root@localhost:27017/'))
    db = client.main
    return db


collection = mongodb_connection().weather

app = Celery('api_parser', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


# create celery task
@app.task
def parse_api(api_url, api_name):
    # parse api
    # save to mongo

    response = requests.get(api_url)
    if not response.status_code == 200:
        raise Exception('API is not available')
    data = response.json()
    mongodb_connection().weather.insert_one({'api_name': api_name, 'data': data})


@app.task
def parse_all_apis():
    for api in apis:
        parse_api.delay(api['api_url'], api['api_name'])
        logging.info(f'{api["api_name"]} is parsed')


apis = [
    {'api_url': 'http://135.181.197.58:8000/api/v1/weather/source_1', 'api_name': 'source_1'},
    {'api_url': 'http://135.181.197.58:8000/api/v1/weather/source_2', 'api_name': 'source_2'},
    {'api_url': 'http://135.181.197.58:8000/api/v1/weather/source_3', 'api_name': 'source_3'},
    {'api_url': 'http://135.181.197.58:8000/api/v1/weather/source_4', 'api_name': 'source_4'},
    {'api_url': 'http://135.181.197.58:8000/api/v1/weather/source_5', 'api_name': 'source_5'},
]

if __name__ == '__main__':
    while True:
        parse_all_apis.delay()
        logging.info('Parsing apis task is created')
        time.sleep(10)
