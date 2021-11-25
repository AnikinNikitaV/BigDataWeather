import json
import os
import re

import pymongo
import matplotlib.pyplot as plt
import numpy as np

cloud_replacements = {
    "sun": "sunny",
    "sunc": "little cloudy",
    "suncl": "cloudy",
    "dull": "dull"
}


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


# Returns sorted by value dictionary of day descriptions in JSON format as keys and number of occurrences as values
def most_frequent_weather(city, start_year=1997, end_year=2021, save_dir=None, data_source="files"):
    weather_combinations = dict()
    day_type = dict()
    discarded = 0
    days = 0
    for year in range(start_year, end_year + 1):
        if data_source == "database":
            data = load_from_database(city, year)
        elif data_source == "files":
            data = load_from_files(city, year)
        else:
            raise ValueError('Invalid argument for argument "data_source" was provided')
            # print(data)
        for month in data["months"]:
            if month:
                # month_numb = month["num"]
                # print(f"\nMonth {month_numb}\n")
                for day in month["days"]:
                    days += 1
                    # Records with missing data are discarded
                    if day["temp"] and day["temp"] != "—" \
                            and day["cloud"] and day["cloud"] != "—" \
                            and day["wind"] and day["wind"] != "—":
                        # Building key based on record data
                        # Temperature and wind speed processed in intervals of length 5.
                        # print(day)
                        day_type["clouds"] = cloud_replacements[day["cloud"]]
                        day_type["extra"] = day["extra"]
                        if day["wind"] == "Ш":
                            day_type["wind"] = "0"
                        else:
                            wind = int(re.search(r'\d+', day["wind"]).group())
                            wind = (wind // 5 + 1) * 5
                            day_type["wind"] = f"{wind - 5}-{wind}"
                        temp = int(day["temp"])
                        if temp >= 0:
                            temp = (temp // 5 + 1) * 5
                            day_type["temp"] = f"{temp - 5}-{temp}"
                        else:
                            temp = (temp // 5 - 1) * 5
                            day_type["temp"] = f"{temp}-{temp + 5}"
                        day_type_key = json.dumps(day_type)
                        # Updating statistic
                        if day_type_key not in weather_combinations.keys():
                            weather_combinations[day_type_key] = 1
                        else:
                            weather_combinations[day_type_key] = weather_combinations[day_type_key] + 1
                    else:
                        discarded += 1
    if save_dir:
        with open(f'..{save_dir}{city} results.json', 'w', encoding='utf-8') as f:
            json.dump(weather_combinations, f, ensure_ascii=False, indent=4)
    # print("\nWeather combinations stats:")
    print(weather_combinations)
    print(days)
    print(discarded)
    return {k: v for k, v in sorted(weather_combinations.items(), key=lambda item: item[1], reverse=True)}


# Returns dictionary of requested weather parameters as keys and lists of year, month and mean value as values.
# period can be "months" or "years", day_time can be "days", "nights" or "all",
# weather_params is list with possible values "wind", "temperature" and "pressure"
def periodic_average_values(city, period, day_time, start_year=1997, end_year=2021, weather_params=None, save_dir=None,
                            data_source="database"):
    if weather_params is None:
        weather_params = []
    result = dict()
    discarded = 0
    days = 0
    pressure_results = []
    temperature_results = []
    wind_results = []
    for year in range(start_year, end_year + 1):
        if data_source == "database":
            data = load_from_database(city, year)
        elif data_source == "files":
            data = load_from_files(city, year)
        else:
            raise ValueError('Invalid argument for argument "data_source" was provided')
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
                    if day["temp"] and day["temp"] != "—" and day["temp"] != "−" \
                            and day["press"] and day["press"] != "—" and day["press"] != "−" \
                            and day["wind"] and day["wind"] != "—" and day["press"] != "−" \
                            and (day_time == "days" and "." not in day["num"]
                                 or day_time == "nights" and "." in day["num"] or day_time == "all"):
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
    print(days)
    print(discarded)
    return result


# Returns dictionary of requested weather parameters as keys and their mean values for specified months from beginning
# of start_year to and end of end_year.
def average_values(city, months=None, start_year=1997, end_year=2021, weather_params=None, save_dir=None,
                   data_source="files"):
    if months is None:
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    if weather_params is None:
        weather_params = ["temperature", "pressure", "wind", "clouds"]
    result = dict()
    days = 0
    mean_pressure = 0
    mean_wind = 0
    mean_temperature = 0
    mean_cloudy_days = 0
    pressure_days = 0
    temp_days = 0
    wind_days = 0
    for year in range(start_year, end_year + 1):
        if data_source == "database":
            data = load_from_database(city, year)
        elif data_source == "files":
            data = load_from_files(city, year)
        else:
            raise ValueError('Invalid argument for argument "data_source" was provided')
        for month in data["months"]:
            if month and int(month["num"]) in months:
                last_cloudy_day = ""
                # month_num = month["num"]
                for day in month["days"]:
                    days += 1
                    if ("wind" in weather_params or not weather_params) \
                            and day["wind"] and day["wind"] != "—" and day["press"] != "−":
                        wind_days += 1
                        if day["wind"] != "Ш":
                            mean_wind += int(re.search(r'\d+', day["wind"]).group())
                    if ("temperature" in weather_params or not weather_params) \
                            and day["temp"] and day["temp"] != "—" and day["temp"] != "−":
                        mean_temperature += int(day["temp"])
                        temp_days += 1
                    if ("pressure" in weather_params or not weather_params) \
                            and day["press"] and day["press"] != "—" and day["press"] != "−":
                        mean_pressure += int(day["press"])
                        pressure_days += 1
                    if "clouds" in weather_params and (day["cloud"] == "suncl" or day["cloud"] == "dull") \
                            and last_cloudy_day != str(day["num"]).split(sep=".")[0]:
                        last_cloudy_day = str(day["num"]).split(sep=".")[0]
                        mean_cloudy_days += 1
    if "pressure" in weather_params or not weather_params:
        result["pressure"] = mean_pressure / pressure_days
    if "temperature" in weather_params or not weather_params:
        result["temperature"] = mean_temperature / temp_days
    if "wind" in weather_params or not weather_params:
        result["wind"] = mean_wind / wind_days
    if "clouds" in weather_params or not weather_params:
        result["clouds"] = mean_cloudy_days / (days / 2)
    if save_dir:
        with open(f'..{save_dir}{city} results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    # print("\nWeather combinations stats:")
    print(days)
    return result


# Returns dictionary of month : [mean day temperature, mean night temperature]
def day_night_temperature(city, start_year=2020, end_year=2021, save_dir=None, data_source="files"):
    result = {
        1: [0, 0],
        2: [0, 0],
        3: [0, 0],
        4: [0, 0],
        5: [0, 0],
        6: [0, 0],
        7: [0, 0],
        8: [0, 0],
        9: [0, 0],
        10: [0, 0],
        11: [0, 0],
        12: [0, 0]
    }
    discarded = 0
    days = 0
    months_days = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for year in range(start_year, end_year + 1):
        if data_source == "database":
            data = load_from_database(city, year)
        elif data_source == "files":
            data = load_from_files(city, year)
        else:
            raise ValueError('Invalid argument for argument "data_source" was provided')
        for month in data["months"]:
            if month:
                month_number = int(month["num"])
                days = month["days"]
                for i in range(0, len(days), 2):
                    if days[i]["temp"] and days[i]["temp"] != "—" and days[i]["temp"] != "−" \
                            and days[i + 1]["temp"] and days[i + 1]["temp"] != "—" and days[i + 1]["temp"] != "−":
                        months_days[month_number - 1] += 1
                        result[month_number][0] += int(days[i]["temp"])
                        result[month_number][1] += int(days[i + 1]["temp"])
    for key in result.keys():
        result[key][0] /= months_days[key - 1]
        result[key][1] /= months_days[key - 1]
    if save_dir:
        with open(f'..{save_dir}{city} results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    return result


def draw_graphics_day_night_temperature(result):
    print(type(result))
    day_temp = []
    night_temp = []
    for key in result.keys():
        day_temp.append(result[key][0])
        night_temp.append(result[key][1])
    plt.plot(list(result.keys()), day_temp, label="день")
    plt.plot(list(result.keys()), night_temp, label="ночь")
    plt.title("День и ночь")
    plt.xlabel("Месяц")
    plt.ylabel("Температура")
    plt.legend()
    plt.show()


# print(load_from_database("Санкт-Петербург", 2020))
# print(periodic_average_values("Санкт-Петербург", "years", "nights"))  # , save_dir="/JSONs/Results/2nd task/"
# print(most_frequent_weather("Санкт-Петербург"))
# print(average_values("Санкт-Петербург", start_year=2001, end_year=2020))
print(day_night_temperature("Санкт-Петербург"))
draw_graphics_day_night_temperature(day_night_temperature("Санкт-Петербург"))

