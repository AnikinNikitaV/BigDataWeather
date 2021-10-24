import requests
import dataclasses
import datetime
import json
import asyncio
import aiohttp
import time

from os import fdopen
from dataclasses import dataclass
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from pathlib import Path

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
    months: list[monthStruct]

async def download_month(y, m):
    try:
        async with aiohttp.ClientSession(headers={'User-Agent': UserAgent().chrome}) as session:
            async with session.get(f'https://www.gismeteo.ru/diary/4079/{y}/{m}/') as resp:
                r = await resp.text()
        if r == "<Response [404]>":
            return None
        else:
            table = BeautifulSoup(r, 'lxml').find_all("table")
            if len(table) == 0:
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

async def download_year(y):
    print(f'Year {y} started')
    months = await asyncio.gather(*[download_month(y,i) for i in range(1, 13)])
    with open(f'../JSONs/{y}.json', 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(yearStruct(months)), f, ensure_ascii=False, indent=4)
    print(f'Year {y} finished')

async def download_all():
    tasks = [asyncio.create_task(download_year(i)) for i in range(1997, datetime.datetime.now().year + 1)]
    await asyncio.gather(*tasks)

print("Started")

try:
    Path("../JSONs").mkdir(parents=True, exist_ok=True)
except:
    raise ValueError('Python cant create folder')

start = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(download_all())
loop.run_until_complete(loop.shutdown_asyncgens())
loop.close()
print("Completed. Process took: {:.2f} seconds".format(time.time() - start))