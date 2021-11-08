import json
import os
import re

cloud_replacements = {
    "sun": "sunny",
    "sunc": "little cloudy",
    "suncl": "cloudy",
    "dull": "dull"
}
# Returns dictionary of day descriptions in JSON format as keys and number of occurrences as values
def most_frequent_weather(city):
    weather_combinations = dict()
    day_type = dict()
    for root, dirs, files in os.walk(f"../JSONs/{city}"):
        if not files:
            raise ValueError('No files to read data from')
        for file in files:
            # print(f"\nYEAR {file}")
            with open(f'../JSONs/{city}/{file}', 'r', encoding='utf-8') as f:
                data = json.load(f)
            # print(data)
            for month in data["months"]:
                if month:
                    month_numb = month["num"]
                    # print(f"\nMonth {month_numb}\n")
                    for day in month["days"]:
                        # Records with missing data are discarded
                        if day["temp"] and day["temp"] != "—" \
                                and day["cloud"] and day["cloud"] != "—" \
                                and day["extra"] and day["extra"] != "—" \
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
    # print("\nWeather combinations stats:")
    print(weather_combinations)
    return weather_combinations


most_frequent_weather("Санкт-Петербург")
# for root, dirs, files in os.walk(f"../JSONs/Санкт-Петербург"):
#     print(dirs)
