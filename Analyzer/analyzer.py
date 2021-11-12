import json
import os

import pymongo


def load_from_files(city, year):
    for root, dirs, files in os.walk(f"../JSONs/{city}"):
        if not files:
            raise ValueError('No files to read data from')
        for file in files:
            file_year = int(file[:4])
            if file_year == year:
                with open(f'../JSONs/{city}/{file}', 'r', encoding='utf-8') as f:
                    return json.load(f)


def load_from_database(city, year):
    client = pymongo.MongoClient('localhost', 27017)
    db = client['Weather']
    collection = db[f"{city}"]
    result = collection.find_one({"num": year})
    return result
