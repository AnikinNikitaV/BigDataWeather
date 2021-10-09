import requests
from bs4 import BeautifulSoup
import datetime
from fake_useragent import UserAgent
import json
from dataclasses import dataclass
import dataclasses
from pathlib import Path

@dataclass
class halfDay:
    temp: str
    press: int
    cloud: str
    extra: str
    wind: str

@dataclass
class dayStruct:
    num: int
    day: halfDay
    evening: halfDay

@dataclass
class monthStruct:
    num: int
    days: list[dayStruct]

@dataclass
class yearStruct:
    months: list[monthStruct]

print("Started")

try:
    Path("../JSONs").mkdir(parents=True, exist_ok=True)
except:
    raise ValueError('Python cant create folder')

years = []
thisYear = datetime.datetime.now().year + 1

try:
    for y in range(1997, thisYear):
        months = []
        for m in range (1, 13):
            try:
                r = requests.get(f'https://www.gismeteo.ru/diary/4079/{y}/{m}/', headers={'User-Agent': UserAgent().chrome})
                if r == "<Response [404]>":
                    break
                else:
                    table = BeautifulSoup(r.text, 'lxml').find_all("table")
                    if len(table) == 0:
                        continue
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
                        month.days.append(dayStruct(day[0], halfDay(*day[1:6]), halfDay(*day[6:11])))
                    months.append(month)
            except:
                raise ValueError(f'Python cant download info. Last year and month: {y, m}')
        with open(f'../JSONs/{y}.json', 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(yearStruct(months)), f, ensure_ascii=False, indent=4)
except:
    raise ValueError('Python cant download or save info')
print("Completed")