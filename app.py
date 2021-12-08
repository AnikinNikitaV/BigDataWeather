import sys #import argv
import os
import argparse
from datetime import datetime
sys.path.append('../Crawler')
sys.path.append('../Analyzer')
sys.path.append('../Graphics')
import crawler
import analyzer
from draw_graphics import drawer



def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-c', '--city', default='Санкт-Петербург')
    parser.add_argument ('-y1', '--year1', default=1997)
    parser.add_argument ('-y2', '--year2', default=2021)
    # parser.add_argument ('-m', '--mongo', default='no')
    parser.add_argument ('-d', '--download', default=None)
    parser.add_argument ('-a', '--analyze', default=None)
    parser.add_argument ('-g', '--graph', default=None)
 
    return parser

p = createParser()
args = p.parse_args(sys.argv[1:])
if args.city != 'all':
    cs = [args.city]
else:
    cs = os.listdir('../JSONs')
    cs.remove('Results')
    # print(c)

if args.download:
    crawler.main()

if args.analyze: #добавить выбор города
    for c in cs:
        analyzer.compare_city_to_climates(city=c, save_dir=True)

if args.graph: #добавить выбор города, графиков
    d = drawer()
    for c in cs:
        if args.graph == '1':
            d.draw_graphic_most_frequent_weather(c, (args.year1), (args.year2), None, "files")
            d.draw_graphics_most_frequent_weather(c, (args.year1), (args.year2), None, "files")
        if args.graph == '2':
            d.draw_graphic_periodic_average_values(c, "years", "days", start_year=(args.year1), end_year=(args.year2))
            d.draw_graphic_periodic_average_values(c, "years", "nights", start_year=(args.year1), end_year=(args.year2))
        if args.graph == '3':
            d.draw_graphics_day_night_temperature(c, start_year=(args.year1), end_year=(args.year2))
            d.draw_graphic_temperatures_compare(c, start_year=(args.year1), end_year=(args.year2))
        if args.graph == 'all':
            d.test(c, int(args.year1), int(args.year2))