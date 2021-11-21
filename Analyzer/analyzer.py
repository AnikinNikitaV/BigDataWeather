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


print(most_frequent_weather("Санкт-Петербург"))
# for root, dirs, files in os.walk(f"../JSONs/Санкт-Петербург"):
#     print(dirs)
