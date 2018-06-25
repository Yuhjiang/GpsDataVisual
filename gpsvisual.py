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


def get_static_map(location, zoom=15, size=(500, 500), scale=0, key=my_key, title=None):
    """
    利用地图API获取地图
    :param location: 中心点位置
    :param zoom: 缩放比例
    :param size: 尺寸
    :param scale: 清晰度，0-高清，1-标清
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
        plt.savefig(fname='title', dpi=300)
    plt.show()


def add_points(origin, destination, color=('red', 'blue'), marker=('O', 'D'), key=_my_key, title=None):
    """
    利用高德API在地图上显示点
    :param origin: 出发点
    :param destination: 到达点
    :param color: 颜色
    :param marker: 标志
    :param key: API的key
    :param title: 图名，若有图名则保存下来
    :return:
    """
    if len(origin) != len(destination):
        raise ValueError('Origin and destination must have the same shape!')

    start = marker[0] + ':' + ';'.join(origin)
    end = marker[1] + ':' + ';'.join(destination)
    url = 'http://restapi.amap.com/v3/staticmap?markers=small,{},{}|small,{},{}&key={}'.format(
        start, colors[color[0]], end, colors[color[1]], key
    )

    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def add_walk_paths(paths, size=(500, 500), weight=5, color='blue', scale=0, key=my_key, title=None):
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
    url = 'http://restapi.amap.com/v3/staticmap?&size={}&paths={},{},1,,:{}&key={}&scale={}'.format(
        size, weight, colors[color], paths, key, scale
    )

    image = get_map(url)
    plt.figure(dpi=300)
    plt.imshow(image)
    plt.axis('off')
    if title:
        plt.title(title)
        plt.savefig(fname=title)
    plt.show()


def add_bus_paths(paths, size=(500, 500), scale=0, key=my_key, title=None):
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
        str_paths.append('{},{},1,,:{}'.format(weight, colors[mode_colors[mode]], ';'.join(points)))
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