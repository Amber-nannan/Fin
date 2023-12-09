# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 10:10:28 2022

@author: Xu Chong
"""

# 本页为爬虫部分需要共用的Function 公式来作为基础模块

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

import akshare as ak

# %%
from Function_mod.basic_module.Trading_date import *
from Function_mod.basic_module.MySQL_related import *
from Function_mod.basic_module.File_related import *

# %%
# 时间相关公式包
# ****************************************************************************************************

token = '4b814b48faeadccaf392445fb500b79b5742b829a439a046971f41a8'
token2 = '009f6a4ab56a90b1bc3218836ff623a250d7e6868d0f4307cd5a3aa7'


# str_type='%Y/%m/%d'  # "%Y%m%d" "%Y-%m-%d"


# 制作相关的时间交易日数据到SQL

def download_sse_trading_date_to_SQL():
    db = 'dbconghua'
    tn = 'sse'
    full_name, engine, con = connect_sql_for_pd(db, tn)

    # 下载交易日数据
    # pro = ts.pro_api(token)#token
    
    trading_date_ = ak.tool_trade_date_hist_sina()#pro.query('trade_cal', start_date='', end_date='', is_open="1")
    
    # 调整交易日数据为日期数据
    # trading_date['cal_date'] = pd.to_datetime(trading_date['cal_date'])
    # trading_date['pretrade_date'] = pd.to_datetime(trading_date['pretrade_date'])
    trading_date = pd.DataFrame()
    trading_date['cal_date']=pd.to_datetime(trading_date_['trade_date'])
    trading_date['pretrade_date']=pd.to_datetime(trading_date_['trade_date']).shift(1)
    trading_date['is_open'] = 1
    trading_date['exchange'] = 'SSE'
    
    # 将数据保存到本地的SQL
    trading_date.to_sql(name=tn, con=con, if_exists='replace', index=False)
    add_primary_key_to_tb_in_SQL(engine, db, tn)


def get_today(str_type):
    today = datetime.date.today().strftime(str_type)
    return today


"""基于当日获取上一个交易日数据
"""


def get_last_tday_share_A_from_today(str_type):
    today = str((datetime.date.today()).strftime("%Y%m%d"))
    d_day = str((datetime.date.today() + datetime.timedelta(days=-12)).strftime("%Y%m%d"))
    pro = ts.pro_api(token)
    last_tday = pro.query('trade_cal', start_date=d_day, end_date='', is_open="1")
    if today in np.array(last_tday['cal_date']):
        print('今天是交易日，数据更新至今天')
        last_tday = today
    else:
        last_tday = last_tday[last_tday['cal_date'] <= today]['cal_date'].max()
        print('今天不是交易日，上一个交易日为')
    last_tday = pd.to_datetime(last_tday).strftime(str_type)
    print(last_tday)
    return last_tday


"""基于指定日期获取上一个交易日数据
"""


def get_last_tday_share_A_from_date(date, str_type):
    date = (pd.to_datetime(date)).strftime("%Y%m%d")
    d_day = str((pd.to_datetime(date) + datetime.timedelta(days=-12)).strftime("%Y%m%d"))
    pro = ts.pro_api(token)
    last_tday = pro.query('trade_cal', start_date=d_day, end_date='', is_open="1")
    if date in np.array(last_tday['cal_date']):
        # print(date+'是交易日')
        last_tday = date
    else:
        last_tday = last_tday[last_tday['cal_date'] <= date]['cal_date'].max()
        # print(date+'不是交易日，上一个交易日为')
    last_tday = pd.to_datetime(last_tday).strftime(str_type)
    print(last_tday)
    return last_tday


"""基于指定日期获取pre交易日数据
"""


def get_pre_tdate_share_A_from_date(date, str_type):
    date = (pd.to_datetime(date)).strftime("%Y%m%d")
    d_day = str((pd.to_datetime(date) + datetime.timedelta(days=-12)).strftime("%Y%m%d"))
    pro = ts.pro_api(token)
    last_tday = pro.query('trade_cal', start_date=d_day, end_date='', is_open="1")
    date_dict = dict(zip(last_tday['cal_date'], last_tday['pretrade_date']))

    if date in np.array(last_tday['cal_date']):
        print(date + '是交易日')
        pre_tday = date_dict[date]
    else:
        pre_tday = last_tday[last_tday['cal_date'] <= date]['cal_date'].max()
        print(date + '不是交易日，上一个交易日为')
        # pre_tday=date_dict[l_tday]

    pre_tday = pd.to_datetime(pre_tday).strftime(str_type)
    print(pre_tday)
    return pre_tday


"""基于指定日期获取下一个交易日数据
"""


# def get_next_tday_share_A_from_date(date, str_type):
#     date = (pd.to_datetime(date)).strftime("%Y%m%d")
#     d_day = str((pd.to_datetime(date) + datetime.timedelta(days=+12)).strftime("%Y%m%d"))
#     pro = ts.pro_api(token)
#     next_tday = pro.query('trade_cal', start_date=date, end_date=d_day, is_open="1")
#     date_dict = dict(zip(next_tday['pretrade_date'], next_tday['cal_date']))

#     if date in np.array(next_tday['pretrade_date']):
#         print(date + '是交易日')
#         next_tdate = date_dict[date]
#     else:
#         next_tdate = next_tday[next_tday['cal_date'] > date]['cal_date'].min()
#         print(date + '不是交易日')
#     next_tdate = pd.to_datetime(next_tdate).strftime(str_type)
#     # print(next_tdate)
#     return next_tdate


"""倒推一定时间的交易日
"""


# def get_time_delta_calender_date(date, delta, str_type):
#     date = (pd.to_datetime(date)).strftime(str_type)
#     date = str(
#         (pd.to_datetime(date) + datetime.timedelta(days=-delta)).strftime(str_type))
#     return date


# def creat_share_A_tr_date_list(start, end, str_type):
#     datestart = (pd.to_datetime(start)).strftime("%Y%m%d")
#     dateend = (pd.to_datetime(end)).strftime("%Y%m%d")
#     pro = ts.pro_api(token)
#     tr_date_list = pro.query(
#         'trade_cal', start_date=str(datestart), end_date=str(dateend), is_open="1")
#     tr_date_list = tr_date_list['cal_date'].to_list()
#     # 改变日期格式
#     tr_date_list = pd.to_datetime(tr_date_list).strftime(str_type).to_list()
#     print('已生成时间列表')
#     return tr_date_list


""" 计算出日历日前推
"""

def get_pre_date_month_from_date(mon, limit_date):
    """
    运算x个月前，及x年前的日期，用于后续运算
    :param mon: int 前推的月份数
    :param limit_date: str 是str格式的时间
    :return: TimeStamp的时间，单个时间
    """
    date_ = pd.Timestamp(limit_date)

    # 当前时间X个月前
    last_m = (int(date_.month) - mon) % 12
    last_y = int((int(date_.year) * 12 + int(date_.month) - mon) / 12)
    if last_m == 0:
        last_m = 12
        last_y = last_y - 1
    # 针对正好是月末状况
    try:
        pre_mon = pd.Timestamp('%s-%s-%s' % (last_y, last_m, date_.day))
    finally:
        pre_mon = datetime.datetime(last_y, last_m + 1, 1) - datetime.timedelta(days=1)
    # last_mon = '%s-%s-%s' % (last_y, last_m,now.day)
    return pre_mon


"""相关的租分类
"""

def get_use_date(use_limit_data, limit_date):
    if use_limit_data:
        use_date = limit_date.strftime('%Y-%m-%d')
    else:
        use_date = get_last_tday_share_A_from_today('%Y-%m-%d')
    return use_date


def get_col_name_sorted(df_to_sort):
    col_name = list(set(df_to_sort))
    col_name.sort(key=list(df_to_sort).index)
    return col_name

def get_pre_date_mth_from_date(mon, limit_date):
    """
    运算x个月前，及x年前的日期，用于后续运算
    :param mon: int 前推的月份数
    :param limit_date: str 是str格式的时间
    :return: TimeStamp的时间，单个时间
    """
    date_ = pd.Timestamp(limit_date)

    # 当前时间X个月前
    last_m = (int(date_.month) - mon) % 12
    last_y = int((int(date_.year) * 12 + int(date_.month) - mon) / 12)
    if last_m == 0:
        last_m = 12
        last_y = last_y - 1
    # 针对正好是月末状况
    try:
        pre_mon = pd.Timestamp('%s-%s-%s' % (last_y, last_m, date_.day))
    except:
        pre_mon = datetime.datetime(last_y, last_m + 1, 1) - datetime.timedelta(days=1)
    # last_mon = '%s-%s-%s' % (last_y, last_m,now.day)
    return pre_mon

return_list = ['YTD', '3M', '6M', '1Y', '3Y', '5Y','max']


def cal_base_date_dict(return_list, use_limit_data, limit_date):
    # 确定基准日：
    use_date = get_use_date(use_limit_data, limit_date)
    
    base_date_dict = {}
    for time_type in return_list:
        # YTD 今年以来设置为今年的1月1日后
        if time_type == 'YTD':
            date_ = pd.Timestamp(use_date)
            base_date_c = pd.Timestamp(datetime.datetime(int(date_.year), 1, 1))
        else:
            # 识别最后一位的类型是年、月的哪一种
            time_freq = time_type[-1]
            del_ = int(time_type[0])
            # 如果是年的情况下倒推12个月，月份可以直接计算
            if time_freq == 'Y':
                del_ = del_ * 12
            # 计算前推的时间
            base_date_c = get_pre_date_mth_from_date(del_, use_date)
        # 装到字典里面去
        base_date_dict[time_type] = base_date_c
    return base_date_dict


from dateutil.relativedelta import relativedelta


def get_report_date(date):
    if isinstance(date, str):
        date_ = pd.to_datetime(date)
    else:
        date_ = date
    year = date_.year
    month = date_.month
    if month in [1, ]:  # 对于1,2,3月底的财务数据采用上一年Q3数据
        year = (date_ - relativedelta(months=12)).year  # 将日期前推12个月
        report_date_ = datetime.date(year, 9, 30)
    elif month in [2, 3, 4]:
        year = (date_ - relativedelta(months=12)).year  # 将日期前推12个月
        report_date_ = datetime.date(year, 12, 31)
    elif month in [5, 6, 7, 8]:
        report_date_ = datetime.date(year, 3, 31)  # 对于8,9月底的财务数据用本年第二季度的数据
    elif month in [9, 10]:
        report_date_ = datetime.date(year, 6, 30)  # 对于8,9月底的财务数据用本年第二季度的数据
    elif month in [11, 12]:
        report_date_ = datetime.date(year, 9, 30)  # 对于10,11,12月底的财务数据用本年第三季度的数据
    return report_date_.strftime('%Y-%m-%d')


# %% 对时间戳进行解码 从一串数字到正常的时间


def unicode_timestamp(timeStamp):
    dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime

# %%
# 从数据库中提取交易日数据：

def get_trading_date_from_mysql():
    """
    从SQL数据库导入交易日期的数据，并生成基础表格

    :return: 生成有交易日期表格及前一个交易日的数据表格
    """
    db = 'dbconghua'
    tn = 'sse'
    full_name, engine, con = connect_sql_for_pd(db, tn)

    # 设置相关读取的内容并且读取表格
    sql = "SELECT * FROM " + \
          tn
    df = pd.read_sql("{}".format(sql), con, index_col='ID')
    
    df.sort_values('cal_date',inplace=True)

    return df


def get_sse_last_tr_date(limit_date):
    """
    根据指定的日期，判断这一天以来的最后一个交易日时间

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定时间限制的情况下的最后一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date)!=str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 如果结束日期是今天，则判断时间是否到晚上10点
    update_hour = 20
    if limit_date == pd.Timestamp(today):
        if datetime.datetime.now().hour <= update_hour:
            limit_date = limit_date + datetime.timedelta(days=-1)

    # 从mysql获得交易日数据
    tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['cal_date'])

    if limit_date in tr_date_list:
            return limit_date

    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        last_tr_day = pd.Timestamp(last_tr_day)
        return last_tr_day

def get_sse_pre_tr_date(limit_date):
    """
    根据指定的日期，判断这一天的前一个交易日

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定日期代码后的上一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date)!=str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 如果结束日期是今天，则判断时间是否到晚上8点

    # 从mysql获得交易日数据
    tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['cal_date'])
    date_dict = dict(zip(tr_date_df['cal_date'],tr_date_df['pretrade_date']))

    if limit_date in tr_date_list:
        pre_tr_date = date_dict[limit_date]
    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        pre_tr_date = date_dict[pd.to_datetime(last_tr_day)]

    return pre_tr_date

def get_sse_next_tr_date(limit_date):
    """
    根据指定的日期，判断这一天以来的之后的一个交易日

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定日期代码后的下一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date)!=str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 如果结束日期是今天，则判断时间是否到晚上8点

    # 从mysql获得交易日数据
    tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['pretrade_date'])
    date_dict = dict(zip(tr_date_df['pretrade_date'], tr_date_df['cal_date']))

    if limit_date in tr_date_list:
        next_tr_date = date_dict[limit_date]
    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        next_tr_date = date_dict[pd.to_datetime(last_tr_day)]

    return next_tr_date

    
def get_last_quarter_day(limit_date):
    lt_date = get_sse_last_tr_date(limit_date)
    # 判断到季度末的时间  
    mth_ = lt_date.month//3
    if mth_>=1 and mth_<=3:
        lrp_date = datetime.date(lt_date.year,mth_*3+1,1) + datetime.timedelta(days=-1)
    elif mth_ ==4:
        lrp_date = datetime.date(lt_date.year+1,1,1) + datetime.timedelta(days=-1)
    else:
        lrp_date = datetime.date(lt_date.year,1,1) + datetime.timedelta(days=-1)
    
    lrp_date = lrp_date.strftime('%Y-%m-%d')
    return lrp_date
    

def get_pre_date_mth_from_date(mon, limit_date):
    """
    运算x个月前，及x年前的日期，用于后续运算
    :param mon: int 前推的月份数
    :param limit_date: str 是str格式的时间
    :return: TimeStamp的时间，单个时间
    """
    date_ = pd.Timestamp(limit_date)

    # 当前时间X个月前
    last_m = (int(date_.month) - mon) % 12
    last_y = int((int(date_.year) * 12 + int(date_.month) - mon) / 12)
    if last_m == 0:
        last_m = 12
        last_y = last_y - 1
    # 针对正好是月末状况
    try:
        pre_mon = pd.Timestamp('%s-%s-%s' % (last_y, last_m, date_.day))
    except:
        pre_mon = datetime.datetime(last_y, last_m + 1, 1) - datetime.timedelta(days=1)
    # last_mon = '%s-%s-%s' % (last_y, last_m,now.day)
    return pre_mon


def get_base_date_dict(limit_date):
    """
    制作根据不同时间维度 'YTD', '3M', '6M', '1Y', '3Y', '5Y'的时间dict出来
    :param limit_date: str
    :return: dict 不同时间对应的具体日期
    """
    # 整理最后一个日期
    use_date = get_sse_last_tr_date(limit_date)

    # 设置时间维度
    cal_date_list = ['YTD', '3M', '6M', '1Y','2Y','3Y']

    # 计算每年的收益率：
    base_date_dict = {}
    for time_type in cal_date_list:
        # YTD 今年以来设置为今年的1月1日后
        if time_type == 'YTD':
            date_ = pd.Timestamp(use_date)
            base_date_c = datetime.datetime(int(date_.year), 1, 1)#- datetime.timedelta(days=1)
            
        else:
            # 识别最后一位的类型是年、月的哪一种
            time_freq = time_type[-1]
            del_ = int(time_type[0])
            # 如果是年的情况下倒推12个月，月份可以直接计算
            if time_freq == 'Y':
                del_ = del_ * 12
            # 计算前推的时间
            base_date_c = get_pre_date_mth_from_date(del_, use_date)
        # 装到字典里面去
        base_date_dict[time_type] = base_date_c

    return base_date_dict


def cal_rp_period(rp_date):
    """
    将一个日期匹配为报告期格式

    Parameters
    ----------
    rp_date : TYPE
        DESCRIPTION.

    Returns
    -------
    rp_period : TYPE
        DESCRIPTION.

    """
    rp_date=pd.Timestamp(rp_date)
    rp_period = str(rp_date.year) + 'Q' + str((rp_date.month - 1) // 3 + 1)
    return rp_period
