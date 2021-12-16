import sys
import os
import json
import matplotlib

sys.path.append('../Analyzer')

import matplotlib.pyplot as plt
# import numpy as np
from analyzer import *

MATRIX_SIZE_X = 5
MATRIX_SIZE_Y = 5
matplotlib.pyplot.switch_backend('Agg')

TO_RUSSIA = {
    "clouds": "облачность",
    "extra": "осадки",
    "wind": "ветер",
    "temp": "температура",
    "pressure": "давление",
    "temperature": "температура",
    "dull": "пасмурно",
    "cloudy": "облачно",
    "sunny": "солнечно",
    "little cloudy": "слегка облачно",
    "snow": "снег",
    "rain": "дождь",
    "storm": "гроза",
}


class drawer_server:
    def __init__(self):
        if not os.path.exists('../Results'):
            os.mkdir('../Results')

    def add_unit(self, text, type):
        res_text = text
        if type == 'wind':
            res_text += " м/с\n"
        elif type == 'temp' or type == "temperature":
            res_text += "\N{DEGREE SIGN}С\n"
        else:
            res_text += "\n"
        return res_text

    def create_label_from_json(self, str):
        res_read_text = ''
        data_in_json = json.loads(str)
        for field in data_in_json:
            if field == 'extra' and data_in_json[field] == '':
                res_read_text += f"{TO_RUSSIA[field]}: нет \n"
            else:
                if data_in_json[field] in TO_RUSSIA:
                    res_read_text += self.add_unit(f"{TO_RUSSIA[field]}: {TO_RUSSIA[data_in_json[field]]}", field)
                else:
                    res_read_text += self.add_unit(f"{TO_RUSSIA[field]}: {data_in_json[field]}", field)
        return res_read_text

    def draw_graphics_most_frequent_weather(self, city, start_year=1997, end_year=2021, save_dir=None,
                                            data_source="files"):
        indicators_weather = ["clouds", "extra", "wind", "temp"]
        weather_combinations = most_frequent_weather(city, start_year=1997, end_year=2021,
                                                     save_dir=None, data_source="files")
        res_image = []
        for indicator in indicators_weather:
            result = {}
            for combination in weather_combinations:
                number = weather_combinations[combination]
                value = json.loads(combination)[indicator]
                if value == "" and indicator == "extra":
                    value = "нет"
                else:
                    if value in TO_RUSSIA:
                        value = self.add_unit(TO_RUSSIA[value], indicator)
                    else:
                        value = self.add_unit(value, indicator)
                old_value = result.get(value)
                if type(old_value) == int:
                    result[value] = number + old_value
                else:
                    result[value] = number
                # print(list(result), list(result.values()))
            plt.figure(figsize=(25, 10))
            plt.bar(list(result), list(result.values()))
            plt.title(f"Наиболее популярные значения по параметру\n{TO_RUSSIA[indicator]} "
                      f"в г. {city} за {start_year}-{end_year} год")
            plt.xlabel("Значение")
            plt.ylabel("Количество повторений")
            # plt.xticks(rotation=45)
            plt.savefig(f"../Results/draw_graphics_most_frequent_weather_{city}_{start_year}_{end_year}_{indicator}")
            res_image.append(f"results/draw_graphics_most_frequent_weather_{city}_{start_year}_{end_year}_{indicator}")
        return res_image

    def draw_graphic_most_frequent_weather(self, city, start_year=1997, end_year=2021, save_dir=None,
                                           data_source="files"):
        weather_combinations = most_frequent_weather(city, start_year=1997, end_year=2021,
                                                     save_dir=None, data_source="files")
        weather_combinations_sample = dict(list(weather_combinations.items())[:MAX_RESULT])
        temp_value = []
        temp_number_repetitions = []
        for key in weather_combinations_sample:
            self.create_label_from_json(key)
            temp_value.append(self.create_label_from_json(key))
            temp_number_repetitions.append(weather_combinations_sample[key])
        plt.figure(figsize=(25, 12))
        plt.bar(temp_value, temp_number_repetitions)
        plt.title(f"Наиболее популярные комбинации погоды в городе {city} за {start_year} - {end_year} год")
        plt.xlabel("Значение")
        plt.ylabel("Количество повторений")
        # plt.xticks(rotation=45)
        plt.savefig(f"../Results/draw_graphic_most_frequent_weather_{city}_{start_year}_{end_year}")
        return [f"results/draw_graphic_most_frequent_weather_{city}_{start_year}_{end_year}"]

    def draw_graphic_periodic_average_values(self, city, period, day_time, start_year=1997, end_year=2021,
                                             weather_params=None, save_dir=None, data_source="files"):
        average_value = periodic_average_values(city, period, day_time, start_year=1997, end_year=2021,
                                                weather_params=None, save_dir=None, data_source="files")
        res_image = []
        for indicator in average_value:
            year, value = zip(*average_value[indicator])
            # print(year, value)
            plt.figure(figsize=(25, 12))
            plt.title(f"Изменение параметра {TO_RUSSIA[indicator]} в г. {city} "
                      f"{start_year}-{end_year}")
            plt.xlabel("Год")
            label_text = self.add_unit("Значение", indicator)
            plt.ylabel(label_text)
            plt.plot(year, value)
            plt.savefig(f"../Results/draw_graphic_periodic_average_values{indicator}_{city}_{start_year}_{end_year}")
            res_image.append(f"results/draw_graphic_periodic_average_values{indicator}_{city}_{start_year}_{end_year}")
        return res_image

    def chose_day_night_temp(self, result):
        day_temp = []
        night_temp = []
        for key in result.keys():
            day_temp.append(result[key][0])
            night_temp.append(result[key][1])
        return day_temp, night_temp

    def draw_graphics_day_night_temperature(self, city, start_year=2020, end_year=2021, save_dir=None,
                                            data_source="files"):
        result = day_night_temperature(city, start_year=2020, end_year=2021, save_dir=None, data_source="files")
        day_temp, night_temp = chose_day_night_temp(result)
        plt.figure(figsize=(25, 12))
        plt.plot(list(result.keys()), day_temp, label="день")
        plt.plot(list(result.keys()), night_temp, label="ночь")
        plt.title(f"Сравнение температур днем и ночью в г.{city} с {start_year}-{end_year}")
        plt.xlabel("Месяц")
        plt.ylabel("Температура \N{DEGREE SIGN}С")
        plt.legend()
        plt.savefig(f"../Results/draw_graphics_day_night_temperature_{city}_{start_year}_{end_year}")
        return [f"results/draw_graphics_day_night_temperature_{city}_{start_year}_{end_year}"]

    def draw_graphic_temperatures_compare(self, city, start_year=1999, end_year=2021, save_dir=None,
                                          data_source="files"):
        index = 1
        fig, axs = plt.subplots(MATRIX_SIZE_X, MATRIX_SIZE_Y, sharex=True, sharey=True, figsize=(25, 12))
        year = start_year
        fig.suptitle(f"Сравнение температур днем и ночью в г.{city} с {start_year}-{end_year}")
        for ax in axs.flat:
            # print(i, ax)
            if year < end_year:
                try:
                    result = day_night_temperature(city, year, year + 1, save_dir, data_source="files")
                    day_temp, night_temp = chose_day_night_temp(result)
                    ax.plot(list(result.keys()), day_temp)
                    ax.set_title(f"{year, year + 1}", fontsize=10, fontweight=10, pad='2.0')
                    ax.plot(list(result.keys()), night_temp)
                    ax.grid()
                    year += 1
                except:
                    print(year)
            else:
                break
        plt.setp(axs[-1, :], xlabel='Месяц')
        plt.setp(axs[:, 0], ylabel='Температура \N{DEGREE SIGN}С')
        plt.savefig(f"../Results/draw_graphic_temperatures_compare_{city}_{start_year}_{end_year}")
        return [f"results/draw_graphic_temperatures_compare_{city}_{start_year}_{end_year}"]

    def test(self, city, year1, year2):
        # ---------------------------task 1------------------------------
        self.draw_graphic_most_frequent_weather(city, year1, year2, None, "files")
        self.draw_graphics_most_frequent_weather(city, year1, year2, None, "files")

        # ---------------------------task 2------------------------------
        self.draw_graphic_periodic_average_values(city, "years", "days", start_year=year1, end_year=year2)
        self.draw_graphic_periodic_average_values(city, "years", "nights", start_year=year1, end_year=year2)

        # ---------------------------task 5------------------------------ new number: 3
        self.draw_graphics_day_night_temperature(city, start_year=year1, end_year=year2)
        self.draw_graphic_temperatures_compare(city, start_year=year1, end_year=year2)


def draw_average(city, start_year=2000, end_year=2020, save_dir=None, data_source="files"):
        values = []
        year = []
        for i in range(start_year, end_year):
            value = average_values(city, i, i + 1, save_dir=None, data_source="files")
            values.append(value)
            year.append(f"{i}-\n{i+1}")
        plt.figure(figsize=(25, 12))
        plt.bar(values, year)
        plt.title(f"{city} за {start_year} - {end_year} год")
        plt.xlabel("Год")
        plt.ylabel(f"Температуры \N{DEGREE SIGN}С")
        plt.savefig(f"../Results/draw_average_{city}_{start_year}_{end_year}")
        return [f"results/draw_average_{city}_{start_year}_{end_year}"]

