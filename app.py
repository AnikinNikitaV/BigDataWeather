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
    parser.add_argument ('-c', '--city', default='all')
    # parser.add_argument ('-m', '--mongo', default='no')
    parser.add_argument ('-d', '--download', default=None)#'simple')
    parser.add_argument ('-a', '--analyze', default=None)#'all')
    parser.add_argument ('-g', '--graph', default=None)#'all')
 
    return parser

p = createParser()
args = p.parse_args(sys.argv[1:])


if args.download:
    print('download')
    crawler.main()

if args.analyze: #добавить выбор города
    print('analyze')
    analyzer.compare_city_to_climates(city='Санкт-Петербург', save_dir=True)

if args.graph: #добавить выбор города, графиков
    print('graphs')
    d = drawer()
    d.test()
    # if args.graph == 1:
    #     print('graph1')
    # if args.graph == 2:
    #     print('graph2')
    # if args.graph == 3:
    #     print('graph3')
    # if args.graph == 4:
    #     print('graph4')