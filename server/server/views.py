from django.http import HttpResponse

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
    drawer_graphic = drawer_server()
    data = drawer_graphic.draw_graphic_most_frequent_weather(city, start_year, end_year)
    return render(' http://127.0.0.1:8000/Results/draw_graphic_most_frequent_weather_'
                  'Альметьевск_1997_2021.png')
