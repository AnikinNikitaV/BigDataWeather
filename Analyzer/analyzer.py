import json
import os
import re

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


# Returns dictionary of requested weather parameters as keys and lists of year, month and mean value as values.
# period can be "months" or "years", day_time can be "days" or "nights",
# weather_params is list with possible values "wind", "temperature" and "pressure"
def average_values(city, period, day_time, start_year=1900, end_year=2100, weather_params=None, save_dir=None):
    if weather_params is None:
        weather_params = []
    result = dict()
    discarded = 0
    days = 0
    pressure_results = []
    temperature_results = []
    wind_results = []
    for root, dirs, files in os.walk(f"../JSONs/{city}"):
        if not files:
            raise ValueError('No files to read data from')
        for file in files:
            year = int(file[:4])
            # print(f"\nYEAR {year}")
            if start_year < year < end_year:
                with open(f'../JSONs/{city}/{file}', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if period == "years":
                    if None in data["months"]:
                        continue
                # print(data)
                period_days = 0
                mean_pressure = 0
                mean_wind = 0
                mean_temperature = 0
                for month in data["months"]:
                    if month:
                        month_num = month["num"]
                        # print(f"\nMonth {month_num}\n")
                        if period == "months":
                            period_days = 0
                            mean_wind = 0
                            mean_temperature = 0
                            mean_pressure = 0
                        for day in month["days"]:
                            days += 1
                            # Records with missing data are discarded, also checks for requested day_time
                            if day["temp"] and day["temp"] != "—" and day["temp"] != "−"\
                                    and day["press"] and day["press"] != "—" and day["press"] != "−"\
                                    and day["wind"] and day["wind"] != "—" and day["press"] != "−"\
                                    and (day_time == "days" and "." not in day["num"]
                                         or day_time == "nights" and "." in day["num"]):
                                period_days += 1
                                # print(day)
                                if "wind" in weather_params or not weather_params:
                                    if day["wind"] != "Ш":
                                        mean_wind += int(re.search(r'\d+', day["wind"]).group())
                                if "temperature" in weather_params or not weather_params:
                                    mean_temperature += int(day["temp"])
                                if "pressure" in weather_params or not weather_params:
                                    mean_pressure += int(day["press"])
                            else:
                                discarded += 1
                        if period == "months":
                            if "pressure" in weather_params or not weather_params:
                                mean_pressure /= period_days
                                pressure_results.append((year, month_num, mean_pressure))
                            if "temperature" in weather_params or not weather_params:
                                mean_temperature /= period_days
                                temperature_results.append((year, month_num, mean_temperature))
                            if "wind" in weather_params or not weather_params:
                                mean_wind /= period_days
                                wind_results.append((year, month_num, mean_wind))
                if period == "years":
                    # print(f"Year {year}, {year_days} days")
                    if "pressure" in weather_params or not weather_params:
                        mean_pressure /= period_days
                        pressure_results.append((year, mean_pressure))
                    if "temperature" in weather_params or not weather_params:
                        mean_temperature /= period_days
                        temperature_results.append((year, mean_temperature))
                    if "wind" in weather_params or not weather_params:
                        mean_wind /= period_days
                        wind_results.append((year, mean_wind))
    if "pressure" in weather_params or not weather_params:
        result["pressure"] = pressure_results
    if "temperature" in weather_params or not weather_params:
        result["temperature"] = temperature_results
    if "wind" in weather_params or not weather_params:
        result["wind"] = wind_results
    if save_dir:
        with open(f'..{save_dir}{city} {period} {day_time} results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    # print("\nWeather combinations stats:")
    print(result)
    print(days)
    print(discarded)
    return result


average_values("Санкт-Петербург", "months", "nights")  # , save_dir="/JSONs/Results/2nd task/")
# for root, dirs, files in os.walk(f"../JSONs/Санкт-Петербург"):
#     print(dirs)
