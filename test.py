# -*- coding=utf-8 -*-
"""
Module:     test
Summary:    测试模块
Author:     Yuhao Jiang
Created:    2018/6/26 Ver.1.0
Updated:
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot
from utils import *
from gpsvisual import *
from utils import key

my_key = key


def test_get_static_map():
    # 获取浙江紫金港校区地图
    zjg = '120.092789,30.305627'
    get_static_map(zjg, zoom=15, size=(500, 500), scale=1, title='紫金港')


def test_walk_route():
    origin = '120.08605,30.309035'
    destination = '120.086245,30.304851'

    distance, duration, paths = get_walk_route(origin, destination)

    print(origin, '到', destination, '的步行距离', distance, '米， 需要', duration, '秒')
    print(paths)

    add_walk_paths(paths, title='步行路径')


def test_bus_route():
    zjg = '120.092789,30.305627'
    yq = '120.124756,30.262339'

    distance, duration, paths = get_bus_route(zjg, yq)

    print(zjg, '到', yq, '的出行距离', distance, '米， 需要', duration, '秒')
    print(paths)

    add_bus_paths(paths, title='公交车路径')


def test_add_points():
    origins = ['120.086721,30.308425', '120.084541,30.302057']
    destinations = ['120.084375,30.308449', '120.083443,30.301998']
    add_points(origins, destinations, title='OD点')

    area = ['120.07912,30.30411', '120.087231,30.297293', '120.092295,30.305333', '120.085429,30.31278']
    add_points_2(origins, destinations, zoom=15, area=area)


def test_heatmap():
    data = pd.read_csv(r'D:\Zhejiang University\Graduate Project\TransMode\Data\new_data.csv')
    longitude = list()
    latitude = list()
    date_lon = {'2018/04/17': [],
                '2018/04/18': [],
                '2018/04/19': [],
                }

    date_lat = {'2018/04/17': [],
                '2018/04/18': [],
                '2018/04/19': [],
                }

    for i, row in data.iterrows():
        gps = row['出发地点经纬度']
        source = row['Source']
        if gps == "('0', '0')":
            continue

        gps = gps.split("', '")
        lon = (float(gps[1][:-2]))
        lat = (float(gps[0][2:]))
        if source == 'Android':
            lon, lat = bd09_to_gcj02(lon, lat)
        if not in_area((lon, lat)):
            continue
        lon, lat = gcj02_to_wgs84(lon, lat)

        longitude.append(lon)
        latitude.append(lat)
        if row['日期'] in ['2018/04/17', '2018/04/18', '2018/04/19']:
            date_lon[row['日期']].append(lon)
            date_lat[row['日期']].append(lat)

    heat_map(longitude, latitude, bins=50, title='all')
    heat_map(date_lon['2018/04/17']*5, date_lat['2018/04/17']*5, bins=50, title='20180417')
    heat_map(date_lon['2018/04/18']*5, date_lat['2018/04/18']*5, bins=50, title='20180418')
    heat_map(date_lon['2018/04/19']*5, date_lat['2018/04/19']*5, bins=50, title='20180419')


def test_create_gif():
    images = ['20180417', '20180418', '20180419']
    create_gif(images, 'all.gif')


if __name__ == '__main__':
    test_get_static_map()
    test_walk_route()
    test_bus_route()
    test_add_points()
    test_heatmap()
    test_create_gif()