import requests
import dataclasses
import pymongo
import datetime
import json
import asyncio
# import aiohttp
import time
import os

from dataclasses import dataclass
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from pathlib import Path
from sys import argv

# @dataclass
# class halfDay:
#     temp: str
#     press: int
#     cloud: str
#     extra: str
#     wind: str

@dataclass
class dayStruct:
    num: float
    temp: str
    press: int
    cloud: str
    extra: str
    wind: str
    # day: halfDay
    # evening: halfDay

@dataclass
class monthStruct:
    num: int
    days: list[dayStruct]

@dataclass
class yearStruct:
    num: int
    months: list[monthStruct]

async def download_month(id, y, m):
    try:
        # Вариант со слишком большой скоростью скорости запросов, ошибка 503
        # async with aiohttp.ClientSession(headers={'User-Agent': UserAgent().chrome}) as session:
        #     async with session.get(f'https://www.gismeteo.ru/diary/4079/{y}/{m}/') as resp:
        #         r = await resp.text()
        r = requests.get(f'https://www.gismeteo.ru/diary/{id}/{y}/{m}/', headers={'User-Agent': UserAgent().chrome})
        if r == "<Response [404]>":
            print("ALARM")
            return None
        else:
            table = BeautifulSoup(r.text, 'lxml').find_all("table")
            if len(table) == 0:
                print("ALARM2")
                return None
            table = table[0]
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            month = monthStruct(m, [])
            for row in rows:
                day = []
                cols = row.find_all('td')
                for ele in cols:
                    imgs = ele.find_all('img')
                    if (len(imgs) != 0) and ("gif" not in imgs[0]["src"]):
                        cloudy = imgs[0]["src"].split("/")
                        day.append(cloudy[len(cloudy)-1].split(".")[0])
                    else:
                        day.append(ele.text.strip())
                month.days.append(dayStruct(day[0], *day[1:6]))
                month.days.append(dayStruct(day[0]+".5", *day[6:11]))
    except:
        raise ValueError(f'Python cant download info. Last year and month: {y, m}')
    return month

async def download_year(name, id, y):
    print(f'Year {y} started')
    months = []
    for i in range(1, 13):
        months.append(await download_month(id,y,i))
    # Вариант со слишком большой скоростью скорости запросов, ошибка 503
    # months = await asyncio.gather(*[download_month(y,i) for i in range(1, 13)])
    with open(f'../JSONs/{name}/{y}.json', 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(yearStruct(y, months)), f, ensure_ascii=False, indent=4)
    print(f'Year {y} finished')

async def download_all(name, id):
    tasks = [asyncio.create_task(download_year(name, id, i)) for i in range(1997, datetime.datetime.now().year + 1)]
    await asyncio.gather(*tasks)

def upload_all():
    client = pymongo.MongoClient('localhost', 27017)
    db = client['Weather']
    for root, dirs, f in os.walk(f"../JSONs"):
        for dir in dirs:
            bulk = []
            path = os.path.join(root, dir)
            files = os.listdir(path)
            for name in files:
                with open(os.path.join(path, name), encoding='utf-8') as file:
                    bulk.append(json.load(file))
            col = db[f"{dir.replace(' ', '_')}"]
            col.drop()
            col.insert_many(bulk)
            
            
def main(download=True, save=False):
    print("Started")
    start = time.time()
    if download:
        try:
            Path("../JSONs").mkdir(parents=True, exist_ok=True)
        except:
            raise ValueError('Python cant create folder')
        with open(Path("./cities.txt"), encoding='utf-8') as file:
            cities = file.readlines()

        for city in cities:
            id, *name = city.split(' ', maxsplit = 1)
            name = name[0].strip('\n').split(', ')[0]
            Path(f"../JSONs/{name}").mkdir(parents=True, exist_ok=True)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(download_all(name, id))
    if save:
        #проверка на существование файлов?
        upload_all()
    print("Completed. Process took: {:.2f} seconds".format(time.time() - start))