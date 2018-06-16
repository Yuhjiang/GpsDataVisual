# -*- coding=utf-8 -*-
"""
Module:     utils
Summary:    存放一些常用函数
Author:     Yuhao Jiang
Created:    2018/6/16  Ver.1.0
"""
import re
import xlwt
import pandas as pd
import math
from math import pi
from geopy.distance import vincenty
import requests
import json
import urllib

# 常量
x_pi = 3.14159265358979324 * 3000.0 / 180.0
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
                  "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
key = 'dd6a138c5da8b9a90c80eddbc42662ea'


def csv2excel(csv_path, excel_path):
    """
    将csv格式数据保存到excel文件中
    :param csv_path: csv路径
    :param excel_path: excel路径
    :return:
    """
    data = pd.read_csv(csv_path)
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)

    # 创建sheet对象
    sheet = book.add_sheet('Main', cell_overwrite_ok=True)

    # 列表名
    columns = data.columns[:]
    for i in range(columns):
        sheet.wirte(0, i, columns[i])

    # 填入数据
    for i in range(data.shape[0]):
        for j in range(len(columns)):
            sheet.wirte(i+1, j, str(data.iloc[i, j+1]))

    book.save(excel_path)


def _transform_long(long, lat):
    """
    初步转换
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    ret = 300.0 + long + 2.0 * lat + 0.1 * long * long + 0.1 * long * lat + 0.1 * math.sqrt(math.fabs(long))
    ret += (20.0 * math.sin(6.0 * long * pi) + 20.0 * math.sin(2.0 * long * pi)) * 2.0 / 3.0
    ret += (20 * math.sin(long * pi) + 40.0 * math.sin(long / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(long / 12.0 * pi) + 300.0 * math.sin(long / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _transform_lat(long, lat):
    """
    初步转换
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    ret = -100.0 + 2.0 * long + 3.0 * lat + 0.2 * lat * lat + 0.1 * long * lat + 0.2 * math.sqrt(math.fabs(long))
    ret += (20.0 * math.sin(6.0 * long * pi) + 20.0 * math.sin(2.0 * long * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def gcj02_to_wgs84(long, lat):
    """
    gcj坐标系转wgs坐标系
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    dlong = _transform_long(long - 105.0, lat - 35.0)
    dlat = _transform_lat(long - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlong = (dlong - 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)

    wglong = long + dlong
    wglat = lat + dlat
    return long * 2 - wglong, lat * 2 - wglat


def bd09_to_gcj02(long, lat):
    """
    bd坐标系转gcj坐标系
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    x = long - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gcjlong = z * math.cos(theta)
    gcjlat = z * math.sin(theta)
    return gcjlong, gcjlat


def bd09_to_wgs84(long, lat):
    """
    bd坐标系转wgs84坐标系
    :param long: 经度
    :param lat: 纬度
    :return:
    """
    long, lat = bd09_to_gcj02(long, lat)
    return gcj02_to_wgs84(long, lat)


def calculate_distance(start_gps, end_gps):
    """
    计算两点直线距离
    :param start_gps: 起始位置
    :param end_gps: 终点位置
    :return:
    """
    url = 'http://restapi.amap.com/v3/distance?origins={}&destination={}&output=json&key={}&type=0'.format(
        start_gps, end_gps, key
    )
    html = requests.get(url, headers=headers)
    text = html.text
    data = json.loads(text)
    distance = data['results'][0]['distance']

    return int(distance)


def get_route(start_gps, end_gps, mode='walk'):
    """
    利用高德地图API获取两点位置信息
    :param start_gps:
    :param end_gps:
    :return: 距离，时间，轨迹
    """
    url = 'http://restapi.amap.com/v3/direction/walking?origin={}&destination={}&key={}'.format(start_gps, end_gps,
                                                                                                key)
    html = requests.get(url, headers=headers)
    text = json.loads(html.text)
    info = text['info']
    if info != 'ok':
        return False

    route = text['route']
    paths = route['paths']

    polylines = []
    distance = 0
    duration = 0
    for path in paths:
        distance = path['distance']
        duration = path['duration']
        steps = path['steps']
        for step in steps:
            polyline = step['polyline']
            for pl in polyline.split(';'):
                polylines.append(pl)

    return int(distance), int(duration), polylines


def get_static_map(location, zoom=10, size=(1024, 1024), paths=None):
    """
    获取静态地图
    :param location: 中心点坐标
    :param zoom: 地图缩放级别
    :param size: 图片宽度×图片高度
    :param paths: 折线
    :return: 静态图片
    """
    zoom = str(zoom)
    size = str(size[0]) + '*' + str(size[1])
    url = 'http://restapi.amap.com/v3/staticmap?location={}&zoom={}&size={}&key={}'.format(location, zoom, size, key)
    bytes = urllib.request.urlopen(url)
    with open('filename' + 'png', 'wb') as f:
        f.write(bytes.read())
        f.flush()
        f.close()


def calculate_axis(point, mid):
    """
    计算两点相对坐标距离
    :param point: 目标点
    :param mid: 中点
    :return: 坐标
    """
    x_point = str(point[0]) + ',' + str(mid[1])
    y_point = str(mid[0]) + ',' + str(point[1])
    x_distance = calculate_distance(x_point, str(mid[0]) + ',' + str(mid[1])) / 2
    y_distance = calculate_distance(y_point, str(mid[0]) + ',' + str(mid[1])) / 2

    if point[0] < mid[0]:
        x = 250 - x_distance
    else:
        x = 250 + x_distance

    if point[1] < mid[1]:
        y = 250 + y_distance
    else:
        y = 250 - y_distance

    return x, y