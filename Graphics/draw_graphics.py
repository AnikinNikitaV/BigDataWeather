import sys
sys.path.append('../Analyzer')

from analyzer import *

MATRIX_SIZE_X = 5
MATRIX_SIZE_Y = 5


def add_unit(text, type):
    res_text = text
    if type == 'wind':
        res_text += " м/с\n"
    elif type == 'temp' or type == "temperature":
        res_text += "\N{DEGREE SIGN}С\n"
    else:
        res_text += "\n"
    return res_text


def draw_graphics_most_frequent_weather(city, start_year=1997, end_year=2021, save_dir=None, data_source="files"):
    indicators_weather = ["clouds", "extra", "wind", "temp"]
    weather_combinations = most_frequent_weather(city, start_year=1997, end_year=2021,
                                                 save_dir=None, data_source="files")
    for indicator in indicators_weather:
        result = {}
        for combination in weather_combinations:
            number = weather_combinations[combination]
            value = json.loads(combination)[indicator]
            if value == "" and indicator == "extra":
                value = "No extra"
            else:
                value = add_unit(value, indicator)
            old_value = result.get(value)
            if type(old_value) == int:
                result[value] = number + old_value
            else:
                result[value] = number
            print(list(result), list(result.values()))
        plt.bar(list(result), list(result.values()))
        plt.title(f"Наиболее популярные значения по параметру {indicator} в г. {city} за {start_year}-{end_year} год")
        plt.xlabel("Значение")
        plt.ylabel("Количество повторений")
        plt.savefig("../Results/draw_graphics_most_frequent_weather")
        plt.show()


def create_label_from_json(str):
    res_read_text = ''
    print(str)
    print(json.loads(str))
    data_in_json = json.loads(str)
    for field in data_in_json:
        print(field)
        if field == 'extra' and data_in_json[field] == '':
            res_read_text += f"{field}: No extra \n"
        else:
            res_read_text += add_unit(f"{field}: {data_in_json[field]}", field)
    return res_read_text


def draw_graphic_most_frequent_weather(city, start_year=1997, end_year=2021, save_dir=None, data_source="files"):
    weather_combinations = most_frequent_weather(city, start_year=1997, end_year=2021,
                                                 save_dir=None, data_source="files")
    weather_combinations_sample = dict(list(weather_combinations.items())[:MAX_RESULT])
    temp_value = []
    temp_number_repetitions = []
    for key in weather_combinations_sample:
        create_label_from_json(key)
        temp_value.append(create_label_from_json(key))
        temp_number_repetitions.append(weather_combinations_sample[key])
    plt.bar(temp_value, temp_number_repetitions)
    plt.title(f"Наиболее популярные комбинации погоды в городе {city} за {start_year} - {end_year} год")
    plt.xlabel("Комбинация погодных параметров")
    plt.ylabel("Количество повторений")
    plt.savefig("../Results/draw_graphic_most_frequent_weather")
    plt.show()


def draw_graphic_periodic_average_values(city, period, day_time, start_year=1997, end_year=2021,
                                         weather_params=None, save_dir=None, data_source="files"):
    average_value = periodic_average_values(city, period, day_time, start_year=1997, end_year=2021,
                                            weather_params=None, save_dir=None, data_source="files")
    for indicator in average_value:
        year, value = zip(*average_value[indicator])
        print(year, value)
        plt.title(f"Изменение параметра {indicator} в г. {city} {start_year}-{end_year}, среднее значение по {period}")
        plt.xlabel("Год")
        label_text = add_unit("Значение", indicator)
        plt.ylabel(label_text)
        plt.plot(year, value)
        plt.savefig(f"../Results/draw_graphic_periodic_average_values{indicator}")
        plt.show()


def chose_day_night_temp(result):
    day_temp = []
    night_temp = []
    for key in result.keys():
        day_temp.append(result[key][0])
        night_temp.append(result[key][1])
    return day_temp, night_temp


def draw_graphics_day_night_temperature(city, start_year=2020, end_year=2021, save_dir=None, data_source="files"):
    result = day_night_temperature(city, start_year=2020, end_year=2021, save_dir=None, data_source="files")
    day_temp, night_temp = chose_day_night_temp(result)
    plt.plot(list(result.keys()), day_temp, label="день")
    plt.plot(list(result.keys()), night_temp, label="ночь")
    plt.title(f"Сравнение температур днем и ночью в г.{city} с {start_year}-{end_year}")
    plt.xlabel("Месяц")
    plt.ylabel("Температура \N{DEGREE SIGN}С")
    plt.legend()
    plt.savefig("../Results/draw_graphics_day_night_temperature")
    plt.show()


def draw_graphic_temperatures_compare(city, start_year=1999, end_year=2021, save_dir=None, data_source="files"):
    index = 1
    fig, axs = plt.subplots(MATRIX_SIZE_X, MATRIX_SIZE_Y, sharex=True, sharey=True)
    year = start_year
    fig.suptitle(f"Сравнение температур днем и ночью в г.{city} с {start_year}-{end_year}")
    for i, ax in enumerate(axs.flat):
        print(i, ax)
        if year < end_year:
            result = day_night_temperature(city, year, year + 1, save_dir, data_source="files")
            day_temp, night_temp = chose_day_night_temp(result)
            ax.plot(list(result.keys()), day_temp)
            ax.set_title(f"{year, year + 1}", fontsize=10, fontweight=10, pad='2.0')
            ax.plot(list(result.keys()), night_temp)
            ax.grid()
            year += 1
        else:
            break
    plt.setp(axs[-1, :], xlabel='Месяц')
    plt.setp(axs[:, 0], ylabel='Температура \N{DEGREE SIGN}С')
    plt.savefig("../Results/draw_graphic_temperatures_compare")
    plt.show()


# ---------------------------task 1------------------------------
draw_graphic_most_frequent_weather("Санкт-Петербург", 1997, 2021, None, "files")
draw_graphics_most_frequent_weather("Санкт-Петербург", 1997, 2021, None, "files")

# ---------------------------task 2------------------------------
draw_graphic_periodic_average_values("Санкт-Петербург", "years", "nights")

# ---------------------------task 5------------------------------
draw_graphics_day_night_temperature("Санкт-Петербург")
draw_graphic_temperatures_compare("Санкт-Петербург")

#

