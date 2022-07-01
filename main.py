import pymongo
from fastapi import FastAPI

from api_parser import mongodb_connection, apis

app = FastAPI()


@app.get("/weather/")
async def weather():
    db = mongodb_connection()
    collection = db.weather
    sources_temperature = dict()
    for s_name in (api['api_name'] for api in apis):
        data = collection.find_one({'api_name': s_name}, sort=[('data.data.last_update', pymongo.DESCENDING)])['data']['data']
        sources_temperature[f'temperature_{s_name}'] = int(data['temperature'][:-2])
    sources_temperature['average_temperature'] = sum(sources_temperature.values()) / len(sources_temperature)
    sources_temperature['min_temperature'] = min(sources_temperature.values())
    sources_temperature['max_temperature'] = max(sources_temperature.values())
    sources_temperature['measurement_system'] = '°C'

    return sources_temperature
