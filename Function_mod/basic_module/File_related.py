# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 11:32:24 2022

@author: Xu Chong
"""
import requests
from lxml import etree
import pandas as pd
import datetime
import pandas as pd
import numpy as np
import inspect
import re
import os
import datetime
import time
import tushare as ts

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import NVARCHAR, Float, Integer
import pymysql

import tushare
# %%
from Function_mod.basic_module.Trading_date import *
from Function_mod.basic_module.MySQL_related import *
from Function_mod.basic_module.File_related import *


# %%

def read_all_excel_csv_in_path(path, dtype):
    file_list = os.listdir(path)

    file_dict = {}
    no = 0
    for file in file_list:
        file_name, file_type = file.split('.')
        if file_type in ['xls', 'xlsx']:
            no += 1
            file_dict[no] = pd.read_excel(path + '/' + file, dtype=dtype)
        if file_type in ['csv']:
            no += 1
            file_dict[no] = pd.read_csv(path + '/' + file, dtype=dtype)

    return file_dict


def get_last_version_in_file(read_path):
    file_list = os.listdir(read_path)
    # 读取文件夹里最后一版文件
    v_list = []
    vn = {}
    raw_data_dict = {}

    for i in file_list:
        j = i.find('.')
        if i[j - 2:j].isdigit() == True:
            v = int(i[j - 2:j])
            vn[v] = i
            v_list.append(int(i[j - 2:j]))

        elif i[j - 1:j].isdigit() == True:
            v = int(i[j - 1:j])
            vn[v] = i
            v_list.append(int(i[j - 1:j]))

    if v_list != []:
        file = vn[max(v_list)]
        path = read_path + file
        
    return path


def read_last_version_in_file(read_path, index, encoding,sheet_name):
    file_list = os.listdir(read_path)
    # 读取文件夹里最后一版文件
    v_list = []
    vn = {}
    raw_data_dict = {}

    for i in file_list:
        j = i.find('.')
        if i[j - 2:j].isdigit() == True:
            v = int(i[j - 2:j])
            vn[v] = i
            v_list.append(int(i[j - 2:j]))

        elif i[j - 1:j].isdigit() == True:
            v = int(i[j - 1:j])
            vn[v] = i
            v_list.append(int(i[j - 1:j]))

    if v_list != []:
        file = vn[max(v_list)]
        path = read_path + file

        if path[path.find('.') + 1:] == 'csv':
            if index == True:
                df = pd.read_csv(path, index_col=0, encoding=encoding, keep_default_na=False)
            else:
                df = pd.read_csv(path, encoding=encoding)

        else:
            if index == True:
                df = pd.read_excel(path, index_col=0, sheet_name =sheet_name,keep_default_na=False)
            else:
                df = pd.read_excel(path, sheet_name =sheet_name,keep_default_na=False)
    return df


