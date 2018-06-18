# -*- coding=utf-8 -*-
"""
Module:     gpsvisual
Summary:    主模块
Author:     Yuhao Jiang
Created:    2018/6/18  Ver.1.0
"""
from utils import *
import matplotlib.pyplot as plt
import matplotlib.image as img
import numpy as np
import pandas as pd


class GpsVisual(object):
    """
    主要模块，用于可视化GPS位置数据
    """
    def __init__(self, location, zoom=15, size=(500, 500), key='dd6a138c5da8b9a90c80eddbc42662ea'):
        self.location = location
        self.zoom = zoom
        self.size = size
        self.key = key

    def static_map(self):
        """
        获取一张静态图
        :return:
        """
        location = self.location
        zoom = str(self.zoom)
        size = str(self.size[0]) + '*' + str(self.size[1])
        url = 'http://restapi.amap.com/v3/staticmap?location={}&zoom={}&size={}&key={}'.format(location, zoom, size,
                                                                                               self.key)
        image = get_static_map(url)
        plt.figure(dpi=300)
        plt.imshow(image)
        plt.axis('off')
        plt.show()

    def add_points(self, start_gps, end_gps):
        """
        利用高德地图API在地图上显示点
        :param start_gps: 出发点GPS
        :param end_gps: 到达点GPS
        :return:
        """
        if len(start_gps) != len(end_gps):
            raise ValueError('Two parameters must have same shape!')

        start = 'O:' + ';'.join(start_gps)
        end = 'D:' + ';'.join(end_gps)
        url = 'http://restapi.amap.com/v3/staticmap?markers=small,0xFF0000,{}|small,0xffa500,{}&key={}'.format(
            start, end, self.key
        )

        image = get_static_map(url)
        plt.figure(dpi=300)
        plt.imshow(image)
        plt.axis('off')
        plt.show()

    def add_paths(self, paths, wegiht=5, color='0x0000FF'):
        """
        增加路径
        :param paths:
        :return:
        """
        paths = ';'.join(paths)
        zoom = str(self.zoom)
        size = str(self.size[0]) + '*' + str(self.size[1])
        url = 'http://restapi.amap.com/v3/staticmap?zoom={}&size={}&paths={},{},1,,:{}&key={}'.format(
            zoom, size, paths, weight, color, self.key
        )
        image = get_static_map(url)
        plt.figure(dpi=300)
        plt.imshow(image)
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    location = '120.08605,30.309035'
    gv = GpsVisual(location, 15, (500, 500))
    #gv.static_map()

    s = ['120.086721,30.308425', '120.084541,30.302057']
    e = ['120.084375,30.308449', '120.083443,30.301998']

    distance, duration, paths = get_route('120.08605,30.309035', '120.086245,30.304851')
    print(paths)
    gv.add_paths(paths)