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
# import MySQLdb

import tushare
#%% 导入自己写的包

from Function_mod.basic_module.Trading_date import *
from Function_mod.basic_module.MySQL_related import *
from Function_mod.basic_module.File_related import *

# import Function_mod.basic_module
# import Function_mod.basic_module.MySQL_related

#%%
# mySQL相关关公式包
#****************************************************************************************************

tushare_token ='4b814b48faeadccaf392445fb500b79b5742b829a439a046971f41a8'


# 1.0 快速读取mySQL并链接相关数据库

def creat_engine_for_db(db):
    engine = create_engine('mysql+pymysql://conghuadb_user:123456@101.132.162.44:3306/'+db)
    return engine
    

def connect_sql_for_pd(database,table_name):
    full_name = database+'.'+table_name
    engine = create_engine('mysql+pymysql://conghuadb_user:123456@101.132.162.44:3306/'+database)
    con = engine.connect()
    return full_name,engine,con



# 2.0 快速删掉一整个mySQL数据，用于全库更新

def mySQL_truncat_table(db,tn):
    full_name,engine,con=connect_sql_for_pd(db,tn)
    # cur  =  con.cursor()
    sql_test='truncate '+tn
    engine.execute(sql_test)
    # con.commit()
    # cur.close()
    # con.close()
    
# 3.0 给数据表增加一个Primary key

def add_primary_key_to_tb_in_SQL(engine,db,tn):
    # full_name,engine,con=connect_sql_for_pd(db,tn)
    engine.execute("""ALTER TABLE `{}`.`{}` \
        ADD COLUMN `ID` INT NOT NULL AUTO_INCREMENT FIRST, \
        ADD PRIMARY KEY (`ID`);""".format(db, tn))
            

def save_concept_data_to_sql(df_temp,db,tn,con,index_col,add_pri_key):
    full_name=db+'.'+tn
    df_temp.to_sql(name=tn, con=con, if_exists='append', index=index_col)
    if add_pri_key:
        add_primary_key_to_tb_in_SQL(engine,db,tn)



"""4.0涉及综合计算
"""
# 4.1 从sql生成A股要更新交易日期

def update_tr_date_list_from_sql(db,tn,str_type): 
    
    try:
        full_name,engine,con=connect_sql_for_pd(db,tn)
        sql_where="SELECT MAX(tr_date) FROM "+full_name+" GROUP BY tr_date;"
        last_date = pd.read_sql("{}".format(sql_where), con).max()[0].strftime(str_type)
        start=get_last_tday_share_A_from_date(last_date,str_type)
        end=get_last_tday_share_A_from_today(str_type)#获取最近一个交易日
        if start==end:
            print('数据库已更新到最近交易日'+start+'，无需更新')
            date_list=[]
        else:
            date_list=creat_share_A_tr_date_list(start,end,str_type)
            print('生成新的时间列表:'+start+'-'+end)
    except:
        print('数据尚无数据，需要完全更新')
        date_list='full'
            
    return date_list

# 4.2 从sql生成要更新的股票列表

def update_stockcode_list_from_sql(db,tn,key,codes): 
    full_name,engine,con=connect_sql_for_pd(db,tn)
    sql_where="SELECT "+key+" FROM "+full_name+" GROUP BY "+key+";"
    stock_list = pd.read_sql("{}".format(sql_where), con)[key].to_list()
    update_stock=set(codes)-set(stock_list)   

    if stock_list==[]:
        print('数据尚无数据，需要完全更新')
    else:
        print('库中已有'+str(len(stock_list))+'个股票')
        print('需要更新'+str(len(update_stock))+'个股票')
    return stock_list,update_stock 


# 4.3 从sql生成要更新的股票列表的基本信息

def save_to_mysql(db, tn, df, method, index_,print_):
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
    
    
