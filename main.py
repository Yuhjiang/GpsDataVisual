# -*- coding=utf-8 -*-
"""
Module:     main
Summary:    主程序
Author:     Yuhao Jiang
Created:    2018/6/19 Ver.1.0
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

file_path = r'D:\Zhejiang University\Graduate Project\TransMode\Data\s_data.csv'
data = pd.read_csv(file_path).iloc[:, 1:]

zjg_area = {
    'latmin': 30.295793,
    'longmin': 120.079911,
    'latmax': 30.310391,
    'longmax': 120.092936,
    'mid': (120.08667,30.304519),
}

def get_zjg_map()