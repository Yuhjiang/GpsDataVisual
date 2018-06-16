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

# 常量
x_pi = 3.14159265358979324 * 3000.0 / 180.0
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
                  "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}


def csv2excel(csv_path, excel_path, headers=True):
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

    if headers:
        columns = data.columns[:]
        for i in range(columns):
            sheet.write(0, i, columns[i])

