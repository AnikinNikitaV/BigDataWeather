from django.http import HttpResponse
import json
from server.draw_graphics_server import drawer_server


def index(request):
    # drawer_graphics = drawer()
    # drawer_graphics.draw_graphic_most_frequent_weather('Москва', 1997, None, "files")
    # print(request.Get('task', ''))
    task = request.GET.get('task', '')
    city = request.GET.get('city', 'Санкт-Петербург')
    start_year = request.GET.get('startYear', '1997')
    end_year = request.GET.get('endYear', '2021')
    print(task, city, start_year, end_year)
    dw = drawer_server()
    data = []
    if task == 'most_frequent_weather':
        data = dw.draw_graphic_most_frequent_weather(city, start_year, end_year)
    elif task == 'most_frequent_weather_all':
        data = dw.draw_graphics_most_frequent_weather(city, start_year, end_year)
    elif task == 'periodic_average_values':
        data = dw.draw_graphic_periodic_average_values(city, "years", "days", start_year, end_year)
    elif task == 'day_night_temperature':
        data = dw.draw_graphics_day_night_temperature(city, start_year, end_year)
    elif task == 'temperatures_compare':
        data = dw.draw_graphic_temperatures_compare(city, start_year, end_year)
    elif task == 'draw_average':
        data = dw.draw_average(city, start_year, end_year)
    print(data)
    res = {
        'img_url': data
    }
    return HttpResponse(json.dumps(res), content_type="application/json")


    # return HttpResponse('http://127.0.0.1:8000/Results/draw_graphic_most_frequent_weather_Альметьевск_1997_2021.png')
    # HttpResponse(json.dumps(res), content_type="application/json")
