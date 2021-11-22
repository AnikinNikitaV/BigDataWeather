import json
import os
import re

import pymongo

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
def most_frequent_weather(city, start_year=1997, end_year=2021, save_dir=None, data_source="database"):
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
def average_values(city, period, day_time, start_year=1997, end_year=2021, weather_params=None, save_dir=None,
                   data_source="database"):
    if weather_params is None:
        weather_params = []
    result = dict()
    discarded = 0
    days = 0
    pressure_results = []
    temperature_results = []
    wind_results = []
    # for root, dirs, files in os.walk(f"../JSONs/{city}"):
    #     if not files:
    #         raise ValueError('No files to read data from')
    #     for file in files:
    #         year = int(file[:4])
    #         # print(f"\nYEAR {year}")
    #         if start_year < year < end_year:
    #             with open(f'../JSONs/{city}/{file}', 'r', encoding='utf-8') as f:
    #                 data = json.load(f)
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
                    if day["temp"] and day["temp"] != "—" and day["temp"] != "−"\
                            and day["press"] and day["press"] != "—" and day["press"] != "−"\
                            and day["wind"] and day["wind"] != "—" and day["press"] != "−"\
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
    print(result)
    print(days)
    print(discarded)
    return result


# print(load_from_database("Санкт-Петербург", 2020))
average_values("Санкт-Петербург", "years", "nights")  # , save_dir="/JSONs/Results/2nd task/")
# for root, dirs, files in os.walk(f"../JSONs/Санкт-Петербург"):
#     print(dirs)


print(most_frequent_weather("Санкт-Петербург"))
# for root, dirs, files in os.walk(f"../JSONs/Санкт-Петербург"):
#     print(dirs)
