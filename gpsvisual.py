# -*- coding=utf-8 -*-
"""
Module:     gpsvisual
Summary:    主模块
Author:     Yuhao Jiang
Created:    2018/6/18  Ver.1.0
Updated:    2018/6/25  Ver.1.1 重构功能
"""
from utils import *
import matplotlib.pyplot as plt
import matplotlib.image as img
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import smopy
from scipy import ndimage
from datetime import datetime
import matplotlib.cm as cm
from utils import headers
import seaborn as sns
sns.set_style('whitegrid', {'font.sans-serif': ['simhei', 'Arial']})

my_key = 'dd6a138c5da8b9a90c80eddbc42662ea'

colors = {
    'black': '0x000000',
    'green': '0x008000',
    'purple': '0x800080',
    'yellow': '0xFFFF00',
    'blue': '0x0000FF',
    'gray': '0x808080',
    'orange': '0xffa500',
    'red': '0xFF0000',
    'white': '0xFFFFFF',
}

mode_colors = {
    'walk': 'blue',
    'bike': 'orange',
    'car': 'red',
    'bus': 'gray',
}


def get_static_map(location, zoom=15, size=(500, 500), scale=1, key=my_key, title=None):
    """
    利用地图API获取地图
    :param location: 中心点位置
    :param zoom: 缩放比例
    :param size: 尺寸
    :param scale: 清晰度，2-高清，1-标清
    :param key: API的key
    :param title: 图名，若有图名则保存下来
    :return:
    """
    zoom = str(zoom)
    size = str(size[0]) + '*' + str(size[1])
    url = 'http://restapi.amap.com/v3/staticmap?location={}&zoom={}&size={}&key={}&scale={}'.format(
        location, zoom, size, key, scale
    )
    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title, dpi=300)
    plt.show()


def add_points(origin, destination, color=('red', 'blue'), marker=('O', 'D'), scale=1, key=my_key, title=None):
    """
    利用高德API在地图上显示点
    :param origin: 出发点
    :param destination: 到达点
    :param color: 颜色
    :param marker: 标志
    :param scale: 清晰度
    :param key: API的key
    :param title: 图名，若有图名则保存下来
    :return:
    """
    if len(origin) != len(destination):
        raise ValueError('Origin and destination must have the same shape!')

    start = marker[0] + ':' + ';'.join(origin)
    end = marker[1] + ':' + ';'.join(destination)
    url = 'http://restapi.amap.com/v3/staticmap?markers=mid,{},{}|mid,{},{}&key={}&scale={}'.format(
        colors[color[0]], start, colors[color[1]], end, key, scale
    )

    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def add_walk_paths(paths, size=(500, 500), weight=5, color='blue', scale=1, key=my_key, title=None):
    """
    利用高德地图绘制步行轨迹
    :param paths: 路径
    :param size: 尺寸
    :param weight: 线宽
    :param color: 颜色
    :param scale: 清晰度
    :param key: API的key
    :param title: 图名，若有图名则保存下来
    :return:
    """
    path = ';'.join(paths)
    size = str(size[0]) + '*' + str(size[1])
    url = "http://restapi.amap.com/v3/staticmap?size={}&paths={},{},1,,:{}&key={}&scale={}".format(
        size, weight, colors[color], path, key, scale
    )

    print(url)
    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def add_bus_paths(paths, size=(500, 500), scale=1, key=my_key, title=None):
    """
    利用高德API绘制公交车路线图
    :param paths: 路径, pandas格式
    :param size: 尺寸
    :param scale: 清晰度
    :param key: API的key
    :param title: 图名
    :return:
    """
    path = list()           # 所有路径
    temp_path = list()      # 子路径
    temp_mode = paths['mode'][0]
    modes = list()
    modes.append(temp_mode)
    for i, row in paths.iterrows():
        gps_point = row['gps']
        mode = row['mode']

        # 出行方式变化，更新路径
        if mode != temp_mode:
            temp_mode = mode
            path.append(temp_path)
            modes.append(temp_mode)
            # 重置子出行路径
            temp_path = list()
            temp_path.append(gps_point)
        else:
            temp_path.append(gps_point)

    path.append(temp_path)

    str_paths = list()
    for i in range(len(modes)):
        mode = modes[i]
        points = path[i]
        str_paths.append('{},{},1,,:{}'.format(5, colors[mode_colors[mode]], ';'.join(points)))
    str_path = '|'.join(str_paths)

    size = str(size[0]) + '*' + str(size[1])
    url = 'http://restapi.amap.com/v3/staticmap?size={}&paths={}&key={}'.format(size, str_path, key)
    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def get_walk_route(origin, destination, key=my_key):
    """
    获取步行路径
    :param origin: 出发点
    :param destination: 到达点
    :param key: API
    :return: 距离，时间，路径
    """
    url = 'http://restapi.amap.com/v3/direction/walking?origin={}&destination={}&key={}'.format(
        origin, destination, key)

    html = requests.get(url, headers=headers)
    text = json.loads(html.text)
    info = text['info']
    if info != 'ok':
        return False

    route = text['route']
    path = route['paths'][0]

    polylines = []
    distance = path['distance']
    duration = path['duration']
    steps = path['steps']
    for step in steps:
        polyline = step['polyline']
        for pl in polyline.split(';'):
            polylines.append(pl)

    return int(distance), int(duration), polylines


def get_bus_route(origin, desination, city='hangzhou', key=my_key):
    """
    获取公交车路径
    :param origin: 出发点
    :param desination: 到达点
    :param city: 城市
    :param key: API
    :return: 距离，时间，路径
    """
    data = pd.DataFrame(columns=['mode', 'gps'])
    modes = list()
    gps = list()
    url = 'http://restapi.amap.com/v3/direction/transit/integrated?origin={}&destination={}&' \
          'city={}&key={}&strategy=5'.format(origin, desination, city, key)
    html = requests.get(url, headers=headers)
    text = json.loads(html.text)
    count = text['count']
    route = text['route']
    distance = route['distance']
    path = route['transits'][0]
    duration = path['duration']
    segments = path['segments']

    for segment in segments:
        walk = segment['walking']['steps']
        for w in walk:
            for point in w['polyline'].split(';'):
                gps.append(point)
                modes.append('walk')

        bus = segment['bus']
        for busline in bus['buslines']:
            for point in busline['polyline'].split(';'):
                gps.append(point)
                modes.append('bus')

    data['gps'] = gps
    data['mode'] = modes
    return int(distance), int(duration), data


def heat_map(longitude, latitude, bins=50, title=None):
    """
    绘制热力图
    :param longitude: 经度
    :param latitude: 纬度
    :param title: 图名
    :return:
    """
    longitude = np.array(longitude)
    latitude = np.array(latitude)
    gps_map = smopy.Map(latitude.min(), longitude.min(), latitude.max(), longitude.max())

    x_lon = gps_map.to_pixels(latitude, longitude)[1]
    y_lat = gps_map.to_pixels(latitude, longitude)[0]

    smoothing = 1
    """
    cmap = LinearSegmentedColormap.from_list('mycmap', [(0, (1, 0, 0, 0)),
                                                        (0.5, (1, 0.5, 0.5, 0.8)),
                                                        (0.75, (1, 1, 0.9, 0.8)),
                                                        (0.875, (1, 1, 1, 1)),
                                                        (1, (1, 1, 1, 1))]
                                             )
    """

    colorlist = ['#5fd9cd', '#eaf786', '#ffb5a1', '#b8ffb8', '#b8f4ff']
    cmap = LinearSegmentedColormap.from_list('mycmap',
                                             [(0, (1, 0, 0, 0)),
                                              (0.5, (1, 0.5, 0, 0.8)),
                                              (0.75, (1, 1, 0, 0.8)),
                                              (0.875, (1, 1, 1, 1)),
                                              (1, (1, 1, 1, 1))
                                              ])

    heatmap, x_edges, y_edges = np.histogram2d(x_lon, y_lat, bins=bins)
    extent = [y_edges[0], y_edges[-1], x_edges[-1], x_edges[0]]
    #logheatmap = np.log(heatmap)
    #logheatmap[np.isneginf(logheatmap)] = 0
    heatmap = ndimage.filters.gaussian_filter(heatmap, smoothing, mode='nearest')

    ax = gps_map.show_mpl(dpi=300)
    ax.imshow(heatmap, cmap=cmap, extent=extent, vmin=0, vmax=10)
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def add_points_2(origin, destination, zoom, area, title=None):
    area_lon, area_lat = str2float(area)
    latMin, lonMin, latMax, lonMax = area_lat.min(), area_lon.min(), area_lat.max(), area_lon.max()
    Map = smopy.Map((latMin, lonMin, latMax, lonMax), z=zoom)
    o_lon, o_lat = str2float(origin)
    d_lon, d_lat = str2float(destination)

    o_x, o_y = Map.to_pixels(o_lat, o_lon)
    ax = Map.show_mpl(figsize=(8, 6))
    ax.plot(o_x, o_y, 'or', ms=5)

    d_x, d_y = Map.to_pixels(d_lat, d_lon)
    ax.plot(d_x, d_y, 'ob', ms=5)

    if title:
        ax.title(title)
        plt.savefig(fname=title, dpi=300)

    plt.show()


def add_area_points(data, zoom, area, title=None):
    longitude = data['longitude'].values
    latitude = data['latitude'].values
    count = data['count'].values
    radius = data['radius'].values

    area_lon, area_lat = str2float(area)
    Map = smopy.Map((area_lat.min(), area_lon.min(), area_lat.max(), area_lon.max()), z=zoom)

    lon = []
    lat = []
    for i in range(len(longitude)):
        m, n = gcj02_to_wgs84(longitude[i], latitude[i])
        lon.append(m)
        lat.append(n)

    lon = np.array(lon)
    lat = np.array(lat)
    x, y = Map.to_pixels(lat, lon)

    shape = [pi * r * r / 8 for r in radius]

    ax = Map.show_mpl(figsize=(8, 8))
    # cm = plt.cm.get_cmap('RdYlBu')
    ax = plt.scatter(x, y, c=count, s=shape, cmap='Reds', alpha=0.5)
    plt.colorbar(ax)

    if title:
        plt.title(title)
        plt.savefig(fname=title, dpi=300)
    plt.show()


if __name__ == '__main__':
    area = {
        '白沙': {
            'location': '120.086705,30.30844',
            'radius': '80',
        },
        '翠柏': {
            'location': '120.086169,30.309612',
            'radius': '80',
        },
        '蓝田': {
            'location': '120.081937,30.309334',
            'radius': '120',
        },
        '丹青': {
            'location': '120.084436,30.309408',
            'radius': '100',
        },
        '云峰': {
            'location': '120.082232,30.307778',
            'radius': '110',
        },
    }

    """
    x = [120.086705, 120.086169, 120.081937, 120.084436, 120.082232]
    y = [30.30844, 30.309612, 30.309334, 30.309408, 30.307778]
    area = ['120.084648,30.307237', '120.080539,30.308932', '120.084788,30.310813', '120.087749,30.30908']
    area_lon, area_lat = str2float(area)

    Map = smopy.Map((area_lat.min(), area_lon.min(), area_lat.max(), area_lon.max()), zoom=15)

    lon = []
    lat = []
    for i in range(len(x)):
        m, n = gcj02_to_wgs84(x[i], y[i])
        lon.append(m)
        lat.append(n)

    lon = np.array(lon)
    lat = np.array(lat)
    x, y = Map.to_pixels(lat, lon)
    area = [pi * r * r / 4 for r in [80, 80, 120, 100, 110]]
    pop = [20, 16, 20, 10, 5]

    ax = Map.show_mpl(figsize=(8, 8))
    # cm = plt.cm.get_cmap('RdYlBu')
    ax = plt.scatter(x, y, c=pop, s=area, cmap='Reds', alpha=0.5)
    plt.colorbar(ax)

    plt.show()
    """
    data = pd.DataFrame(columns=['longitude', 'latitude', 'count', 'radius'])
    area = ['120.084648,30.307237', '120.080539,30.308932', '120.084788,30.310813', '120.087749,30.30908']
    data['longitude'] = [120.086705, 120.086169, 120.081937, 120.084436, 120.082232]
    data['latitude'] = [30.30844, 30.309612, 30.309334, 30.309408, 30.307778]
    data['count'] = [20, 16, 20, 10, 5]
    data['radius'] = [80, 80, 120, 100, 110]
    add_area_points(data, zoom=15, area=area)