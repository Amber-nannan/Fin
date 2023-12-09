# -*- coding: utf-8 -*-
"""
Created on Thu May 19 12:09:06 2022

@author: Xu Chong
"""

# %% 导入必要的python module
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties

import pandas as pd
import numpy as np
import datetime
import math
from sklearn import preprocessing
from scipy import stats
import statsmodels as sm
import sklearn.linear_model  # 做回归用的
from openpyxl import load_workbook

import matplotlib.pyplot as plt
from matplotlib import ticker
import seaborn as sns

import inspect
import re
import os
# from WindPy import *
import random
from sklearn.metrics import r2_score
# import tushare

# %% 导入一些用于多个基础公式的模块文件
from Function_mod.basic_module.File_related import *
from Function_mod.basic_module.MySQL_related import *
from Function_mod.basic_module.Trading_date import *

# 用于单一爬虫eastmoney的指数数据
# from Function_mod.cal_module.concept_industry_index_fun import *


# %% part1 更新CREITs的底层basic_info数据
today = datetime.datetime.today().strftime('%Y-%m-%d')

full_name, engine, con = connect_sql_for_pd('dbconghua', 'basic_info')
sql = f"SELECT * FROM {full_name}"
r_info = pd.read_sql("{}".format(sql), con, index_col='ID')
r_info_ = r_info.set_index('reit_code')
r_info_.sort_values(by=['REITs_type_L1', 'REITs_type_L2'], inplace=True)

sorted_codes = r_info_.sort_values(by=['REITs_type_L1', 'REITs_type_L2']).index.to_list()
sorted_names = r_info_.sort_values(by=['REITs_type_L1', 'REITs_type_L2'])['REITs_name'].to_list()
sorted_types = ['公募REITs'] + \
               r_info_['REITs_type_L1'].drop_duplicates().to_list() + \
               r_info_['REITs_type_L2'].drop_duplicates().to_list()

fin_ttm_dict = {
    'FFO': 'PFFO',
    'NI': 'PE',
    'CFO': 'PCFO',
    'EBITDA': 'EV/EBITDA',
    'distributable_amount(period)': 'Pdiv',
    'nav': 'PB'
}

fin_ttm_rev_dict = {
    'FFO': 'FFOP',
    'NI': 'EP',
    'CFO': 'CFOP',
    'EBITDA': 'EBITDA_to_EV',
    'distributable_amount(period)': 'div_yield',
    'nav': 'BP'
}

fin_ttm_list = fin_ttm_dict.keys()


# 设置相关读取的内容并且读取表格

# %% 导入wind的数据包

def connect_wind():
    w.start()  # 命令超时时间为120秒
    w.start(waitTime=30)  # 命令超时时间设置成60秒
    print(w.start())

    # w.stop()  # 当需要停止WindPy时，可以使用该命令
    # 注： w.start不重复启动，若需要改变参数，如超时时间，用户可以使用w.stop命令先停止后再启动。
    # 退出时，会自动执行w.stop()，一般用户并不需要执行w.stop

    w.isconnected()  # 即判断WindPy是否已经登录成功


# %% 获取相关从mysql获取的数据
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
    sql = "SELECT * FROM " + tn
    df = pd.read_sql("{}".format(sql), con, index_col='ID')
    df.sort_values('cal_date', inplace=True)

    return df


tr_date_df = get_trading_date_from_mysql()

def get_tr_date_list(start_date,end_date):
    tr_date_df = get_trading_date_from_mysql()
    df_time = tr_date_df[
        (tr_date_df['cal_date'] >=pd.to_datetime(start_date)) &
        (tr_date_df['cal_date'] <=pd.to_datetime(end_date))]['cal_date']
    result = df_time.sort_values().to_list()
    return result

def get_sse_last_tr_date(limit_date):
    """
    根据指定的日期，判断这一天以来的最后一个交易日时间

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定时间限制的情况下的最后一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date) != str:
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
    # tr_date_df = get_trading_date_from_mysql()
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
    if type(limit_date) != str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 如果结束日期是今天，则判断时间是否到晚上8点
    # 从mysql获得交易日数据
    # tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['cal_date'])
    date_dict = dict(zip(tr_date_df['cal_date'], tr_date_df['pretrade_date']))

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
    if type(limit_date) != str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 从mysql获得交易日数据
    # tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['pretrade_date'])
    date_dict = dict(zip(tr_date_df['pretrade_date'], tr_date_df['cal_date']))

    if limit_date in tr_date_list:
        next_tr_date = date_dict[limit_date]
    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        next_tr_date = date_dict[pd.to_datetime(last_tr_day)]

    return next_tr_date


def get_sse_next_n_tr_date(ndays, limit_date):
    """
    根据指定的日期，判断这一天以来的之后的一个交易日

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定日期代码后的下一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date) != str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today

    # 如果结束日期是今天，则判断时间是否到晚上8点

    # 从mysql获得交易日数据
    # tr_date_df = get_trading_date_from_mysql()
    tr_date_list = np.array(tr_date_df['pretrade_date'])
    date_dict = dict(zip(tr_date_df['cal_date'], tr_date_df['cal_date'].shift(-ndays)))

    if limit_date in tr_date_list:
        next_tr_date = date_dict[limit_date]
    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        next_tr_date = date_dict[pd.to_datetime(last_tr_day)]

    return next_tr_date


def get_sse_pre_n_tr_date(ndays, limit_date):
    """
    根据指定的日期，判断这一天之前的n个交易日

    :param limit_date: str 输入的时间限制，不输入则默认为今天
    :return: 输出指定日期代码后的下一个交易日
    """
    # 获取今天的时间
    today = pd.Timestamp(datetime.date.today())

    # 将时间从字符串转化为时间,并且将没有输入时间的，自动设置为今天
    if type(limit_date) != str:
        limit_date = pd.Timestamp(limit_date)
    elif len(limit_date) != 0:
        limit_date = pd.Timestamp(limit_date)
    else:
        limit_date = today
    # 从mysql获得交易日数据
    tr_date_list = np.array(tr_date_df['pretrade_date'])
    date_dict = dict(zip(tr_date_df['cal_date'], tr_date_df['cal_date'].shift(ndays-1)))

    if limit_date in tr_date_list:
        pre_tr_date = date_dict[limit_date]
    else:
        last_tr_day = tr_date_list[tr_date_list <= limit_date][-1]
        pre_tr_date = date_dict[pd.to_datetime(last_tr_day)]
    return pre_tr_date


def get_last_quarter_day(limit_date):
    lt_date = get_sse_last_tr_date(limit_date)
    # 判断到季度末的时间
    mth_ = lt_date.month // 3
    if mth_ >= 1 and mth_ <= 3:
        lrp_date = datetime.date(lt_date.year, mth_ * 3 + 1, 1) + datetime.timedelta(days=-1)
    elif mth_ == 4:
        lrp_date = datetime.date(lt_date.year + 1, 1, 1) + datetime.timedelta(days=-1)
    else:
        lrp_date = datetime.date(lt_date.year, 1, 1) + datetime.timedelta(days=-1)

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


def get_base_date_with_select(ndays):
    if ndays in ['YTD', '3M', '6M', '1Y', '2Y', '3Y']:
        base_date_dict = get_base_date_dict('')
        return base_date_dict[ndays]
    elif ndays in ['max', 'MAX']:
        return pd.Timestamp('2021-06-21')
    elif type(ndays)!=int:
        return pd.Timestamp(ndays)
    else:
        return get_sse_pre_n_tr_date(ndays, '')


def cal_rp_period(rp_date):
    rp_date = pd.Timestamp(rp_date)
    rp_period = str(rp_date.year) + 'Q' + str((rp_date.month - 1) // 3 + 1)
    return rp_period

def rp_period_to_date(rp_period):
    year = int(rp_period[:4])
    quarter = int(rp_period[5])
    if quarter == 4:
        next_year = year + 1
        next_quarter = 1
    else:
        next_year = year
        next_quarter = quarter + 1
    next_month = (next_quarter - 1) * 3 + 1
    next_day = 1
    next_date = datetime.datetime(next_year, next_month, next_day)
    rp_date = next_date - datetime.timedelta(days=1)
    return rp_date.strftime('%Y-%m-%d')


# %% part 2 dbconghua - SQL数据库相关代码

# 2.1 保存基础数据到dbconghua
def save_to_mysql(db, tn, df, method, index_, print_):
    """
    一般的保存到mysql的一个公式
    :param db: str，database的名字
    :param tn: str, table name
    :param df: DataFrame，要保存的表格
    :param method: str,'append' 还是’replace‘
    :param index_: bool, TRUE 还是False 要不要index
    :return: 没有什么结果，就是保存到sql了
    """
    # db = 'dbconghua'
    # tn = 'basic_info'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    df.to_sql(name=tn, con=con, if_exists=method, index=index_)
    if print_:
        print('数据已经保存到%s - %s' % (db, tn))
    try:
        add_primary_key_to_tb_in_SQL(engine, db, tn)
    except:
        pass


# 2.2 适用于对一个sql进行自己写的sql_w的封装（读取）：
def excute_sqlw_read(db, tn, sql_w, index_col='ID'):
    full_name, engine, con = connect_sql_for_pd(db,tn)
    # sql_w = f"SELECT * FROM {full_name} where reit_code = '{code}' "
    df = pd.read_sql("{}".format(sql_w), con, index_col=index_col)
    return df

# 2.3 适用于对一个sql进行自己写的sql_w的封装（操作）：
def excute_sqlw(db,tn,sql_w):
    full_name, engine, con = connect_sql_for_pd(db,tn)
    # sql_w = 'DELETE FROM ' + full_name + ' WHERE ID in %s' % str(sel1)
    return engine.execute("{}".format(sql_w))
    

# ======对于数据库中某一个factor得到最终的交易日期

def check_last_factor_ltr(factor, tn):
    db = 'dbconghua'
    # tn = 'factor_data'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    sel_f_tosql = 'factor_name=' + "\'" + factor + "\'"
    sql_w = "SELECT reit_code,tr_date FROM " + \
            full_name + ' where ' + sel_f_tosql + \
            " GROUP BY reit_code,tr_date;"
    # 尝试读取sql有没有这个数据
    try:
        result = pd.read_sql("{}".format(sql_w), con)
        if result.empty:
            exist_code = set()
            last_date = "2021-06-20"
            print('目前库中REITs尚未更新,需要更新该数据')
        else:
            last_date = result['tr_date'].max()
            exist_code = set(result['reit_code'])
            print('目前库中的REITs共' + str(len(exist_code)) + '个')

    except Exception as e:
        print('目前不存在该数据库，重新更新')
        exist_code = set()
        last_date = "2021-06-20"
    print('*' * 50)
    print(factor + '数据库最后日期为:' + str(last_date))

    return last_date


def update_from_last_factor_ltr(factor, tn, df):
    last_date = check_last_factor_ltr(factor, tn)
    df = df[df['tr_date'] > pd.Timestamp(last_date)]
    return df


# %% part3 CREIT_采用读取SQL后再匹配内容


def sql_list_trans(m_list):
    sel1 = tuple(m_list)
    if len(sel1) == 1:
        sel1 = str(tuple(sel1)).replace(',', '')
    return sel1


# 从数据库变成交叉表格
def restrucutre_creits_data(factor, con, full_name, restructrue):
    sel_f_tosql = 'factor_name=' + "\'" + factor + "\'"
    sql_w = "SELECT * FROM " + \
            full_name + ' where ' + sel_f_tosql
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')
    # result = result[~result['reit_code'] =='ErrorReport']

    df = result.pivot_table(index=['tr_date'], columns=['reit_code'],
                            values=['data'], dropna=False)
    df.columns = df.columns.levels[1]
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df


# 从交叉表格按照一个名字保存到mysql使用，其中factor_name_是要保存的名字
# 适用于基本所有的market_data类，用到tr_date的
def restructure_data_into_mysql_df(df, factor_name_):
    # df_ = pd.DataFrame()
    # for reit_code in df.columns:
    #     df_res = pd.DataFrame()
    #     df_res['data'] = df[reit_code]
    #     df_res['tr_date'] = df.index.copy()
    #     df_res['reit_code'] = reit_code
    #     df_res['factor_name'] = factor_name_
    #     df_ = pd.concat([df_, df_res], axis=0)
    #     df_.reset_index(drop=True, inplace=True)
    df.index.name='tr_date'
    df_=df.reset_index().melt(id_vars=['tr_date'],
                           value_vars=df.columns,
                           var_name='reit_code',
                           value_name='data')
    df_['factor_name']=factor_name_
    return df_


def match_all_reits_datain_info(mv, limit_date, date_relate):
    db = 'dbconghua'
    tn = 'basic_info'
    full_name, engine, con = connect_sql_for_pd(db, tn)

    # 设置相关读取的内容并且读取表格
    sql = f"SELECT * FROM {tn}"
    r_info = pd.read_sql("{}".format(sql), con, index_col='ID')
    r_info_ = r_info.set_index('reit_code')

    mv['REITs_type_L1'] = mv['reit_code'].map(r_info_['REITs_type_L1'])
    mv['REITs_type_L2'] = mv['reit_code'].map(r_info_['REITs_type_L2'])
    mv['REITs_name'] = mv['reit_code'].map(r_info_['REITs_name'])
    if date_relate:
        mv['rp_period'] = mv['tr_date'].map(lambda x: cal_rp_period(x))
        mv = mv[mv['tr_date'] <= get_sse_last_tr_date(limit_date)]
    return mv


def get_creits_sql_basedate_data(factor_list, base_date, tn, restructure):
    """
    取出指定日期以后的data
    """

    # 1> 连接数据库
    db = 'dbconghua'
    # tn = 'fund_flow'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    # df = restrucutre_creits_data(factor, con, full_name)

    # 2> 通过数据库得到数据
    sel1 = sql_list_trans(factor_list)  # list转化成一个tuple
    sel1_ = 'factor_name in %s' % str(sel1)

    sel2 = f"tr_date >= '{base_date}'"

    # sel_f_tosql = 'factor_name=' + "\'" + factor + "\'"
    sql_w = "SELECT * FROM " + \
            f'{full_name} where {sel1_} and {sel2}'
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')

    # 3> 重构关于相关的数据结构
    if len(factor_list) <= 1:
        if restructure:
            df = result.pivot_table(index=['tr_date'], columns=['reit_code'],
                                    values=['data'], dropna=False)
            df.columns = df.columns.levels[1]
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            return df
        else:
            return result
    else:
        # print('多个因子不能进行重构')
        return result


# 这个用于大部分的dataframe
def get_creits_sql_data(factor_list, tn, restructure):
    """
    是有一个factor list的情况下进行restructure，tn是选择因子的哪一个表格时用的
    """
    # 1> 连接数据库
    db = 'dbconghua'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    # 2> 通过数据库得到数据
    sel1 = sql_list_trans(factor_list)  # list转化成一个tuple
    sel1_ = 'factor_name in %s' % str(sel1)
    sql_w = f"SELECT * FROM {full_name} where {sel1_}"
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')

    # 3> 重构关于相关的数据结构
    time_col = 'rp_date' if (tn in ['fin_data','fin_data_a','q_rp_date']) else 'tr_date'
        
    if len(factor_list) <= 1:
        if restructure:
            df = result.pivot_table(index=[time_col], columns=['reit_code'],
                                    values=['data'], dropna=False)
            df.columns = df.columns.levels[1]
            if tn != 'temp_period_return':
                df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            return df
        else:
            return result
    else:
        return result

def get_creits_sql_data_last(factor_list, tn):
    """
    获取tn数据库中这个factor_list的最后一天的数据
    factor_list --> list eg.['market_cap', 'market_cap_float']
    tn --> str eg.'market_data' 数据库的
    """
    
    db = 'dbconghua'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    time_col = 'rp_date' if (tn in  ['fin_data','fin_data_a','q_rp_date']) else 'tr_date'
    # 2> 通过数据库得到数据
    sel1 = sql_list_trans(factor_list)  # list转化成一个tuple
    sel1_ = 'factor_name in %s' % str(sel1)
    sql_w = f"SELECT * FROM {full_name} where {sel1_} and"+\
        f" {time_col} = (SELECT MAX({time_col}) FROM {full_name})"
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')

    return result



# 【财报】获得对应的factor的财报数据，是否要重构可选
def get_creits_fin_data(factor, restructure):
    db = 'dbconghua'
    tn = 'fin_data'
    full_name, engine, con = connect_sql_for_pd(db, tn)

    sel_f_tosql = 'factor_name=' + "\'" + factor + "\'"
    sql_w = "SELECT * FROM " + \
            full_name + ' where ' + sel_f_tosql
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')

    if restructure:
        df = result.pivot_table(index=['rp_date'], columns=['reit_code'],
                                values=['data'], dropna=False)
        df.columns = df.columns.levels[1]
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    else:
        return result


# 【benchmark】这个是benchmark表格的读取方法    
def get_benchmark_factor_df(factor_name, ben_select):
    full_name, engine, con = connect_sql_for_pd('dbconghua', 'benchmark_data')

    # 变成sql语言中需要的tuple
    sel1 = str(tuple(ben_select))
    if len(ben_select) == 1:
        sel1 = sel1.replace(',', '')

    sql_where = "SELECT tr_date,ben_name,%s FROM %s " % (factor_name, full_name) + \
                "where ben_name in %s" % sel1
    # last_date = pd.read_sql("{}".format(sql_where), con).max()[0].strftime(str_type)
    result = pd.read_sql("{}".format(sql_where), con)

    df = result.pivot_table(index=['tr_date'], columns=['ben_name'],
                            values=[factor_name], dropna=False)

    df.columns = df.columns.levels[1]
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    # df.fillna(0, inplace=True)

    return df


# 选择有限数量REITs的名字
def get_creits_sql_data_sel_reits(factor_list, reits_list, tn, restructure):
    """
    是有一个factor list的情况下进行restructure，
    tn是选择因子的哪一个表格时用的
    否则不能进行重构

    Parameters
    ----------
    factor_list : TYPE
        DESCRIPTION.
    """

    # 1> 连接数据库
    db = 'dbconghua'
    # tn = 'fund_flow'
    full_name, engine, con = connect_sql_for_pd(db, tn)
    # df = restrucutre_creits_data(factor, con, full_name)

    # 2> 通过数据库得到数据
    sel1 = sql_list_trans(factor_list)  # list转化成一个tuple
    sel1_ = 'factor_name in %s' % str(sel1)
    sel2 = sql_list_trans(reits_list)  # list转化成一个tuple
    sel2_ = 'reit_code in %s' % str(sel2)
    # sel_f_tosql = 'factor_name=' + "\'" + factor + "\'"
    sql_w = f"SELECT * FROM {full_name} where {sel1_} and {sel2_}"
    result = pd.read_sql("{}".format(sql_w), con, index_col='ID')

    # 3> 重构关于相关的数据结构
    time_col = 'rp_date' if (tn in 
                             ['fin_data','fin_data_a','q_rp_date']) else 'tr_date'
    if len(factor_list) <= 1:
        if restructure:
            df = result.set_index([time_col,'reit_code'])['data'].unstack()
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            return df
        else:
            return result
            print('多个因子不能进行重构')
    else:
        return result


# =====基础数据库相关打包操作,会放到factor_data
def check_and_save_factor_data_insql(df1, rb_name, col_style, tn):
    """
    进行数据库要的格式的重构，并且检查数据库之后填入数据库
    Parameters
    ----------
    df1 : TYPE
        DESCRIPTION.
    rb_name : 这个是factor的name
    col_style : name,code两个模式
    """
    # 2> 对df1进行restructure然后放入数据库
    df2 = pd.DataFrame()
    df = pd.DataFrame()
    for i in df1.columns:
        df['data'] = df1[i].copy()
        if col_style == 'name':
            df['reit_code'] = dict(zip(r_info['REITs_name'], r_info['reit_code']))[i]
        else:
            df['reit_code'] = i
        df['factor_name'] = rb_name
        df2 = pd.concat([df2, df], axis=0)
    df2.reset_index(drop=False, inplace=True)
    df2.rename(columns={"index": "tr_date"}, inplace=True)

    # 进行原来日期和factor的更新时间
    try:
        df2 = update_from_last_factor_ltr(rb_name, tn, df2)
    except:
        print('数据库尚未建立，更新建立')

    save_to_mysql('dbconghua', tn, df2, 'append', False, True)

# %% 根据type选择代码

# 用于对应类别拿出相应的股票代码
def get_selected_codes(r_type_,codes):
    if len(codes)==0:
        if r_type_ in ['all','公募REITs']:
            codes = r_info_
        else:
            if type(r_type_) == str:
                r_type_ = [r_type_]
            codes = r_info_[r_info_['REITs_type_L1'].isin(r_type_) | 
                            r_info_['REITs_type_L2'].isin(r_type_)]
        codes = codes.index.to_list()
    return codes

# 适用于多选的情况
def get_selected_multi_codes(r_type,codes):
    # r_type 是有2个以上r_type_的情况
    if type(r_type)==str:
        r_type = [r_type]
    if len(codes)==0:
        codes = []
        for r_type_ in r_type:
            codes_ = get_selected_codes(r_type_,codes)
            codes = codes + codes_
    return codes


# %% 进行数据库内的数据去重

def drop_duplicate_mysql(db,tn,firstorlast):
    full_name, engine, con = connect_sql_for_pd('dbconghua', 'basic_info')
    sql_w = f'SELECT * FROM {db}.{tn}'
    df = excute_sqlw_read(db, tn, sql_w, index_col='ID')
    origin_id = df.index.to_list()
    df2 = df.drop_duplicates(keep=firstorlast)
    new_id = df2.index.to_list()
    del_id = list(set(origin_id)-set(new_id))

    if del_id == []:
        print('数据库需要不需要进行去重')
    else:
        sel1 = tuple(del_id)
        if len(sel1) == 1:
            sel1 = str(tuple(sel1)).replace(',', '')
        sql = f'DELETE FROM {db}.{tn} WHERE ID in %s' % str(sel1)
        con.execute("{}".format(sql))
        print('数据库需要进行去重，去重数量为%d条' % len(del_id))
    return len(del_id)



# 用于删除某一列的名字等于这个东西的时候
def delete_specific_data_mysql(del_col, del_name, tn, con):
    full_name = f'dbconghua.{tn}'

    # sel_query = f"SELECT COUNT(*) FROM {full_name} WHERE {del_col} = '{del_name}'"
    # pd.read_sql("{}".format(sel_query), con)
    delete_query = f"DELETE FROM {full_name} WHERE {del_col} = '{del_name}'"
    try:
        result = con.execute("{}".format(delete_query))
        del_num = result.rowcount
        print(f"已删除数据库中{del_col}为{del_name}的数据{del_num}条")
    except:
        print(f'还没有{full_name}数据库存在')


def delete_to_update_mysql(df_, del_col, del_name, tn, con):
    full_name = f'creits.{tn}'
    delete_specific_data_mysql(del_col, del_name, tn, con)
    insert_ = df_.to_sql(name=tn, con=con, if_exists='append', index=False)
    print(f'已在数据库中重新更新{del_name}的数据{insert_}条')
    try:
        add_primary_key_to_tb_in_SQL(engine, 'dbconghua', tn)
    except:
        pass


# %% 制作数据对应的图片

def matplot_simple_pic(df1, chart_type, title):
    myfont = FontProperties(fname=r'C:/WINDOWS/Fonts/MSJH.TTC', size=10)

    rc = {'font.sans-serif': 'Microsoft JhengHei UI',
          'axes.unicode_minus': False,
          # 'figure.facecolor': '#FFFFFF',
          # 'axes.facecolor': '#FFFFFF',
          'legend.title_fontsize': 7,
          # 'title.font.weight':'bold'
          }
    sns.set(rc=rc, font=myfont.get_name())
    sns.set_theme(style="dark", rc=rc,
                  font=myfont.get_name(), font_scale=1.5)
    df1.plot(
        kind=chart_type, title=title,
        xlabel='', figsize=(16, 10))


def matplot_simple_pic_white(df1, chart_type, title, l=16, v=10):
    myfont = FontProperties(fname=r'C:/WINDOWS/Fonts/MSJH.TTC', size=10)

    rc = {'font.sans-serif': 'Microsoft JhengHei UI',
          'axes.unicode_minus': False,
          # 'figure.facecolor': '#FFFFFF',
          # 'axes.facecolor': '#FFFFFF',
          'legend.title_fontsize': 7,
          # 'title.font.weight':'bold'
          }
    sns.set(rc=rc, font=myfont.get_name())
    sns.set_theme(style="white", rc=rc,
                  font=myfont.get_name(), font_scale=1.5)
    df1.plot(
        kind=chart_type, title=title,
        xlabel='', figsize=(16, 10))


# %% 字典操作相关

# 1> 反向查抄字典
def get_keys_from_value(dictionary, value):
    keys = []
    for key, val in dictionary.items():
        if val == value:
            keys.append(key)
    return keys

# 2> 合并相关字典


# %%
