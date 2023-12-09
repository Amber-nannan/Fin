# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 13:57:01 2023

@author: Xu Chong
"""
# %% 导入自己写的库

from Function_mod.basic_creits_date_sql import *
# from Fin_rp.main import *

# %% 获取原始报表
import pandas as pd
# 获取初步的原始报表
def read_standeard_mgt_fee(path):
    # path = 'Fin_rp/mgt_fee/Quarterly_mgt_fee'
    # 'C_REITs/Fin_rp/Quarterly_report'
    file_list = os.listdir(path)
    file_dict = {}
    no = 0
    for file in file_list:
        file_name, file_type = file.split('.')
        if file_type in ['xls', 'xlsx']:
            no += 1
            mgt_fee_df = pd.read_excel(
                path + '/' + file, skiprows=1, index_col=0)#.iloc[:, :-6]
            mgt_fee_df.dropna(subset=mgt_fee_df.columns[1:], how='all', inplace=True)
            for col in mgt_fee_df.columns:
                if mgt_fee_df[col].dtype == 'object':
                    mgt_fee_df[col] = mgt_fee_df[col].str.replace(
                        ',', '').str.replace('\n', '').str.replace('-', '').\
                        replace('',np.nan).astype(float)
            file_dict[file_name] = mgt_fee_df.copy()
    return file_dict

# %% 季度管理费的清洗

# 1> 匹配市场数据
def get_market_rp_data(mgt_fee, rp_date, rp_period):
    if 'Q' in rp_period:
        suffix=''
    elif 'H' in rp_period:
        suffix = '_h'
    elif 'A' in rp_period:
        suffix = '_a'
    metrics_=get_creits_sql_data(['nav','revenue','unit_total'],'fin_data'+suffix,False)
    df = metrics_[metrics_['rp_date']==rp_date]
    df = df.reset_index().set_index(['reit_code','factor_name'])['data'].unstack().dropna()
    df['book_value'] = df['unit_total']*df['nav']
    df = df.reindex(mgt_fee.index)
    return df

# %%
# 3>清洗相关的列名
def rename_creits_q_mgt_fee(mgt_fee_df, rp_date):
    mgt_fee = pd.DataFrame(index=mgt_fee_df.index)
    mgt_fee_df['rp_date'] = rp_date
    # mgt_fee_df['REITs_name'] = r_info_['REITs_name']  # 这一行是什么东西

    fac_dict = {
        '基金管理人计提管理费': 'mgt_fee_for_fm',
        '计划管理人计提管理费': 'mgt_fee_for_pm',
        '基金和计划管理人管理费合计': 'mgt_fee_fm_plus_pm',
        '基金托管人计提托管费': 'custody_fee_for_fm',
        '计划管理人计提托管费': 'custody_fee_for_pm',
        '基金和ABS托管人托管费合计': 'custody_fee',
        '外部管理机构计提固定管理费': 'fixed_mgt_fee_for_ext_org',
        '外部管理机构计提浮动管理费': 'float_mgt_fee_for_ext_org',
        '外部机构管理费合计': 'mgt_fee_for_ext_org',
    }

    mgt_fee_ = mgt_fee_df[fac_dict.keys()].copy()
    mgt_fee_.columns = mgt_fee_.columns.map(fac_dict)
    mgt_fee = pd.concat([mgt_fee, mgt_fee_], axis=1)       #为什么mgt_fee也留着

    # 对数据进行简单计算合并
    mgt_fee['mgt_fee_fm_plus_pm'] = mgt_fee['mgt_fee_fm_plus_pm'].combine_first(
        mgt_fee['mgt_fee_for_fm'].add(mgt_fee['mgt_fee_for_pm'], fill_value=0))
    
    mgt_fee['mgt_fee_for_ext_org'] = mgt_fee['mgt_fee_for_ext_org'].combine_first(
        mgt_fee['fixed_mgt_fee_for_ext_org'].add(mgt_fee['float_mgt_fee_for_ext_org'], fill_value=0))
    mgt_fee['mgt_fee_for_ext_org'].fillna(0, inplace=True)

    mgt_fee['custody_fee'] = mgt_fee['custody_fee'].combine_first(
        mgt_fee['custody_fee_for_fm'].add(mgt_fee['custody_fee_for_pm'], fill_value=0))

    mgt_fee['total_mgt_fee']=mgt_fee['mgt_fee_fm_plus_pm'].add(mgt_fee['mgt_fee_for_ext_org'],fill_value=0)
    mgt_fee['total_fund_struct_costs']=mgt_fee['total_mgt_fee'].add(mgt_fee['custody_fee'],fill_value=0)
    mgt_fee['compr_costs_paid_to_ext_org'] = mgt_fee['mgt_fee_for_ext_org']
    return mgt_fee


# 消去两种方式计算的差值
def offset_diff_func(row):
    diff = row['total_mgt_fee']-row['total_mgt_fee_a']
    if round(abs(diff),2) > 0: 
        if abs(diff - row['mgt_fee_for_ext_org'])<1e-5:  
            # 这种diff来源于text里有外部机构管理费，而table里的浮动管理费为空
            row['mgt_fee_for_ext_org']=0
        elif diff < row['total_mgt_fee_a']/10:
            # 这种diff差得比较小，把diff塞到外部机构管理费里抹平
            row['mgt_fee_for_ext_org']-=diff
        row['total_mgt_fee'] = row['mgt_fee_fm_plus_pm']+row['mgt_fee_for_ext_org']
        row['total_fund_struct_costs'] = row['total_mgt_fee']+row['custody_fee']
    return row


# 4>计算metrics相关的数据，并且生成metrics
def cal_creits_mgt_fee_metrics(mgt_fee, rp_date, rp_period):
    metrics = get_market_rp_data(mgt_fee, rp_date, rp_period)
    rp_type_ = re.findall(r"[a-zA-Z]", rp_period)[0]

    if rp_type_!='Q':
        mgt_fee=mgt_fee.apply(offset_diff_func,axis=1)
        metrics['fixed_mgt_fee_prop']=mgt_fee['fixed_mgt_fee']/mgt_fee['total_mgt_fee']
        metrics['float_mgt_fee_prop']=mgt_fee['float_mgt_fee']/mgt_fee['total_mgt_fee']
        metrics['fixed_mgt_fee_to_total_struct_costs']=mgt_fee['fixed_mgt_fee']/mgt_fee['total_fund_struct_costs']
        metrics['float_mgt_fee_to_total_struct_costs']=mgt_fee['float_mgt_fee']/mgt_fee['total_fund_struct_costs']
        metrics['custody_fee_to_total_struct_costs']=mgt_fee['custody_fee']/mgt_fee['total_fund_struct_costs']
        metrics['client_maint_fee_to_fixed_mgt_fee']=mgt_fee['client_maint_fee']/mgt_fee['fixed_mgt_fee']
    else:
        metrics['custody_fee_to_total_struct_costs']=mgt_fee['custody_fee']/mgt_fee['total_fund_struct_costs']
    # 各主体管理费占比
    mgt_fee['diff']= mgt_fee['compr_costs_paid_to_ext_org']-mgt_fee['mgt_fee_for_ext_org']
    metrics['diff_to_total_mgt_fee']= mgt_fee['diff']/mgt_fee['total_mgt_fee']
    metrics['mgt_fee_for_fm_prop']= mgt_fee['mgt_fee_for_fm']/mgt_fee['total_mgt_fee']
    metrics['mgt_fee_for_pm_prop']= mgt_fee['mgt_fee_for_pm']/mgt_fee['total_mgt_fee']
    metrics['mgt_fee_fm_plus_pm_prop']= mgt_fee['mgt_fee_fm_plus_pm']/mgt_fee['total_mgt_fee']
    metrics['mgt_fee_for_ext_org_prop']= mgt_fee['mgt_fee_for_ext_org']/mgt_fee['total_mgt_fee']

    # 提取出常用指标
    rev = metrics['revenue']
    nav = metrics['book_value']     
    # rev系列和nav系列
    fee_series = ['total_fund_struct_costs', 
                         'custody_fee', 
                         'total_mgt_fee', 
                         'mgt_fee_for_fm', 
                         'mgt_fee_for_pm', 
                         'mgt_fee_for_ext_org',
                         'mgt_fee_fm_plus_pm',
                         'diff']
    fee_series = fee_series if rp_type_=='Q' else fee_series+['fixed_mgt_fee','float_mgt_fee']
    for series in fee_series:
        metrics[f'{series}_to_rev'] = mgt_fee[series] / rev
        metrics[f'{series}_to_nav'] = mgt_fee[series] / nav
    return mgt_fee,metrics


# 5>清洗相关的数据
def res_mgt_fee_tosql(mgt_fee,rp_period):
    res_fin = mgt_fee.stack().to_frame('data').reset_index()
    res_fin.columns = ['reit_code','factor_name','data']
    res_fin['rp_period'] = rp_period
    res_fin['rp_date'] = rp_period_to_date(rp_period)
    return res_fin
            

# 6>计算相关的季度增长率数据（环比）
def cal_QOQ_mgt_fee_data(mgt_fee, base_qoq,str_):
    list1 = ['mgt_fee_for_fm', 'mgt_fee_for_pm',
                    'mgt_fee_for_ext_org', 'custody_fee', 
                    'total_mgt_fee','total_fund_struct_costs']
    list2 = ['fixed_mgt_fee','float_mgt_fee','client_maint_fee']
    cal_list = list1 if 'Q' in str_ else list1+list2
    
    df_qoq = mgt_fee[cal_list].copy()
    try:
        df_qoq_ = df_qoq / base_qoq - 1
        df_qoq_.columns = df_qoq_.columns + str_
        # print(df_yoy_)
    except:
        print('开始计算相关指标qoq')
    base_qoq = df_qoq.copy()
    mgt_fee = pd.concat([mgt_fee, df_qoq_], axis=1)
    return mgt_fee, base_qoq

# 计算增长率（季度的同比）
def cal_YOY_mgt_fee_data(mgt_fee, base_yoy,str_):
    list1 = ['mgt_fee_for_fm', 'mgt_fee_for_pm',
                    'mgt_fee_for_ext_org', 'custody_fee', 
                    'total_mgt_fee','total_fund_struct_costs']
    # list2 = ['fixed_mgt_fee','float_mgt_fee','client_maint_fee']
    cal_list = list1
    
    df_yoy = mgt_fee[cal_list].copy()
    base_yoy = mgt_fee[cal_list].copy()
    df_yoy_ = df_yoy / base_yoy - 1
    df_yoy_.columns = df_yoy_.columns + str_
    mgt_fee = pd.concat([mgt_fee, df_yoy_], axis=1)
    return mgt_fee


"""
主要生成公式
"""

def update_quarterly_fund_mgt_fee_in_mysql():
    file_dict = read_standeard_mgt_fee(r'mgt_fee\Quarterly_mgt_fee')
    base_qoq = pd.DataFrame()
    # # reits_close = creits_data['close_bfq'].T.copy()
    for file in file_dict.keys():
        mgt_fee_df = file_dict[file]
        rp_period = file[:6]
        rp_date = rp_period_to_date(rp_period)  # 按照PDF作出调整
        print(rp_period, rp_date)

        # 1> 将原始财务报表重新进行因子化改名
        mgt_fee = rename_creits_q_mgt_fee(mgt_fee_df, rp_date)

        # 2> 计算相关的主要REITs_metrics
        mgt_fee, metrics_rp = cal_creits_mgt_fee_metrics(mgt_fee, rp_date,rp_period)

        # 3> 计算相关的季度Q-o-Q数据（环比）
        mgt_fee, base_qoq = cal_QOQ_mgt_fee_data(mgt_fee, base_qoq,'_QoQ')
        
        # 4> 计算相关的季度Y-o-Y数据（同比）
        rp_date2 = (pd.to_datetime(rp_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
        rp_period2 = cal_rp_period(rp_date2)
        file2 = file.replace(rp_period,rp_period2)
        if file2 in file_dict.keys():
            mgt_fee_df2 = file_dict[file2]
            mgt_fee2 = rename_creits_q_mgt_fee(mgt_fee_df2,rp_date2)
            mgt_fee = cal_YOY_mgt_fee_data(mgt_fee, mgt_fee2,'_YoY')
        else:
            print('不存在上一年同期数据，无法计算环比')

        # 5> restructure_data到便于保存到sql数据库
        res_mgt_fee = res_mgt_fee_tosql(mgt_fee,rp_period)
        res_metrics = res_mgt_fee_tosql(metrics_rp,rp_period)
        res_ = pd.concat([res_mgt_fee, res_metrics], axis=0)
        res_ = res_[res_['data'] != float('inf')]
        print("%s 管理费数据更新完毕" % file)

        # 6> 洗好的数据，放到sql中进行更新
        # 数据库基础链接，并抽取最后一版的数据
        db = 'dbconghua'
        tn = 'fund_mgt_fee_q'
        full_name, engine, con = connect_sql_for_pd(db, tn)
        delete_to_update_mysql(res_, 'rp_period', rp_period, tn, con)

# %% 年报的清洗及更新

def rename_creits_A_mgt_fee(mgt_fee_df, rp_date):
    mgt_fee = pd.DataFrame(index=mgt_fee_df.index)
    # 改名字的规则
    fac_dict = {
        '基金管理人计提管理费': 'mgt_fee_for_fm',
        '计划管理人计提管理费': 'mgt_fee_for_pm',
        '基金和计划管理人管理费合计': 'mgt_fee_fm_plus_pm',
        '基金托管人计提托管费': 'custody_fee_for_fm',
        '计划管理人计提托管费': 'custody_fee_for_pm',
        '基金和ABS托管人托管费合计': 'custody_fee',
        '外部管理机构计提固定管理费': 'fixed_mgt_fee_for_ext_org',
        '外部管理机构计提浮动管理费': 'float_mgt_fee_for_ext_org',
        '外部机构管理费合计': 'mgt_fee_for_ext_org',
        '当期发生的基金应支付的管理费':'total_mgt_fee_a', # !!!!
        '固定管理费':'fixed_mgt_fee',
        '浮动管理费':'float_mgt_fee',
        '支付销售机构的客户维护费':'client_maint_fee',
        '当期发生的基金应支付的托管费':'custody_fee_a'
    }

    mgt_fee_ = mgt_fee_df[fac_dict.keys()].copy()
    mgt_fee_.columns = mgt_fee_.columns.map(fac_dict)
    mgt_fee = pd.concat([mgt_fee, mgt_fee_], axis=1)     

    # 对数据进行简单计算合并
    mgt_fee['mgt_fee_fm_plus_pm'] = mgt_fee['mgt_fee_fm_plus_pm'].combine_first(
        mgt_fee['mgt_fee_for_fm'].add(mgt_fee['mgt_fee_for_pm'], fill_value=0))
    
    mgt_fee['mgt_fee_for_ext_org'] = mgt_fee['mgt_fee_for_ext_org'].combine_first(
        mgt_fee['fixed_mgt_fee_for_ext_org'].add(mgt_fee['float_mgt_fee_for_ext_org'], fill_value=0))
    mgt_fee['mgt_fee_for_ext_org'].fillna(0, inplace=True)

    mgt_fee['custody_fee'] = mgt_fee['custody_fee'].combine_first(
        mgt_fee['custody_fee_for_fm'].add(mgt_fee['custody_fee_for_pm'], fill_value=0))

    mgt_fee['total_mgt_fee']=mgt_fee['mgt_fee_fm_plus_pm'].add(mgt_fee['mgt_fee_for_ext_org'],fill_value=0)
    mgt_fee['total_fund_struct_costs']=mgt_fee['total_mgt_fee'].add(mgt_fee['custody_fee'],fill_value=0)
    mgt_fee['compr_costs_paid_to_ext_org'] = mgt_fee['mgt_fee_for_ext_org']
    return mgt_fee

def update_annual_fund_mgt_fee_in_mysql():
    file_dict = read_standeard_mgt_fee(r'mgt_fee\Annual_mgt_fee')
    base_yoy = pd.DataFrame()
    for file in file_dict.keys():
        mgt_fee_df = file_dict[file]
        rp_period = file[:5]
        rp_date = rp_period_to_date(rp_period)  # 按照PDF作出调整
        print(rp_period, rp_date)
        # 1> 将原始财务报表重新进行因子化改名
        mgt_fee = rename_creits_A_mgt_fee(mgt_fee_df, rp_date)
        # 2> 计算相关的主要REITs_metrics
        mgt_fee, metrics_rp = cal_creits_mgt_fee_metrics(mgt_fee, rp_date,rp_period)
        # 4> 计算相关的季度Y-o-Y数据
        mgt_fee, base_yoy = cal_QOQ_mgt_fee_data(mgt_fee, base_yoy,'_YoY')
    
        # 5> restructure_data到便于保存到sql数据库
        res_mgt_fee = res_mgt_fee_tosql(mgt_fee,rp_period)
        res_metrics = res_mgt_fee_tosql(metrics_rp,rp_period)
        res_ = pd.concat([res_mgt_fee, res_metrics], axis=0)
        res_ = res_[res_['data'] != float('inf')]
        print("%s 管理费数据更新完毕" % file)
        
        db = 'dbconghua'
        tn = 'fund_mgt_fee_a'
        full_name, engine, con = connect_sql_for_pd(db, tn)
        delete_to_update_mysql(res_, 'rp_period', rp_period, tn, con)
    

# %% 半年报的清洗
def update_midterm_fund_mgt_fee_in_mysql():
    file_dict1 = read_standeard_mgt_fee(r'mgt_fee\Midterm_mgt_fee')
    file_dict2 = read_standeard_mgt_fee(r'mgt_fee\Annual_mgt_fee')
    
    base_hoh = pd.DataFrame()
    base_yoy1 = pd.DataFrame()
    base_yoy2 = pd.DataFrame()

    cal_yoy={}
    for file in file_dict1.keys():
        mgt_fee_df = file_dict1[file]
        rp_period = file if 'Mid' not in file else file[:4]+'H1'
        rp_date = rp_period_to_date(rp_period)  # 按照PDF作出调整
        print(rp_period, rp_date)
        # 1> 将原始财务报表重新进行因子化改名
        mgt_fee = rename_creits_A_mgt_fee(mgt_fee_df, rp_date)
        mgt_fee, metrics_rp = cal_creits_mgt_fee_metrics(mgt_fee, rp_date,rp_period)
        mgt_fee, base_hoh = cal_QOQ_mgt_fee_data(mgt_fee, base_hoh,'_HoH')
        mgt_fee, base_yoy1 = cal_QOQ_mgt_fee_data(mgt_fee, base_yoy1,'_YoY')

        res_mgt_fee = res_mgt_fee_tosql(mgt_fee,rp_period)
        res_metrics = res_mgt_fee_tosql(metrics_rp,rp_period)
        res_ = pd.concat([res_mgt_fee, res_metrics], axis=0)
        res_ = res_[res_['data'] != float('inf')]

        db = 'dbconghua'
        tn = 'fund_mgt_fee_h'
        full_name, engine, con = connect_sql_for_pd(db, tn)
        delete_to_update_mysql(res_, 'rp_period', rp_period, tn, con)

        # 2> 计算整年的数据
        rp_period2 = file[:4]+'H2'
        rp_date2 = rp_period_to_date(rp_period2)  # 按照PDF作出调整
        # 3> 对于整年的年报拆分中报
        try:
            mgt_fee_df2 = file_dict2[file[:4]+'AMgmt']
            mgt_fee_df2 = mgt_fee_df2.reindex(mgt_fee.index)
            mgt_fee2 = rename_creits_A_mgt_fee(mgt_fee_df2, rp_date2)

            period_col = ['mgt_fee_for_fm', 'mgt_fee_for_pm', 'mgt_fee_fm_plus_pm', 
                          'custody_fee_for_fm', 'custody_fee_for_pm', 'custody_fee', 
                          'fixed_mgt_fee_for_ext_org', 'float_mgt_fee_for_ext_org', 
                          'mgt_fee_for_ext_org', 'total_mgt_fee_a', 'fixed_mgt_fee', 
                          'float_mgt_fee', 'client_maint_fee', 'custody_fee_a',
                          'total_mgt_fee','total_fund_struct_costs','compr_costs_paid_to_ext_org']
            mgt_fee2_ = mgt_fee2[period_col] - mgt_fee[period_col]
            mgt_fee2.update(mgt_fee2_)
            
            mgt_fee2, metrics_rp2 = cal_creits_mgt_fee_metrics(mgt_fee2, rp_date2,rp_period2)
            mgt_fee2, base_hoh = cal_QOQ_mgt_fee_data(mgt_fee2, base_hoh,'_HoH') #HOH是共用的
            mgt_fee2, base_yoy2 = cal_QOQ_mgt_fee_data(mgt_fee2, base_yoy2,'_YoY') #YOY是不共用的

            # 3> restructure_data到便于保存到sql数据库
            print(rp_period2,rp_date2)
            res_mgt_fee2 = res_mgt_fee_tosql(mgt_fee2,rp_period2)
            res_metrics2 = res_mgt_fee_tosql(metrics_rp2,rp_period2)
            res_2 = pd.concat([res_mgt_fee2, res_metrics2], axis=0)
            res_2 = res_2[res_2['data'] != float('inf')]
            delete_to_update_mysql(res_2, 'rp_period', rp_period2, tn, con)
            # mgt_fee2=metrics_rp2=res_2 = pd.DataFrame()

        except:
            print(f'暂无{file[:4]}H2数据')
            mgt_fee2=metrics_rp2=res_2 = pd.DataFrame()

        print("%s与 %s管理费数据更新完毕" % (rp_period,rp_period2))



#%% 
update_quarterly_fund_mgt_fee_in_mysql()
# update_annual_fund_mgt_fee_in_mysql()
# update_midterm_fund_mgt_fee_in_mysql()