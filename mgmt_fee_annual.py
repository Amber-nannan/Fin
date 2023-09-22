import re
from pathlib import Path
import pandas as pd

# %% 管理费
# -*- coding: UTF-8 –*-
import re
def get_mf1(s):
    mf1=re.search('计提基金管理人管理费([\d\W]+)元',s)
    if mf1:
        return mf1.group(1)
    elif re.search('基金管理人的管理费计提金额([\d\W]+)元',s):
        mf1=re.search('基金管理人的管理费计提金额([\d\W]+)元',s).group(1)
    elif re.search('基金管理人(?:计提|收取)?的?(?:基金)?管理费共?为?([\d\W万]+)元',s):
        mf1=re.search('基金管理人(?:计提|收取)?的?(?:基金)?管理费共?为?([\d\W万]+)元',s).group(1)
    elif re.search('报告期内发生应支付基金管理人的管理费([\d\W]+)元',s):
        mf1=re.search('报告期内发生应支付基金管理人的管理费([\d\W]+)元',s).group(1)
        mf1=''
    return mf1

def get_mf2(s):
    mf2=re.search('资产支持证券管理人(?:收取)?的?管理费为?([\d\W]+)元',s)
    if mf2:
        return mf2.group(1)
    elif re.search('资产支持证券管理人的管理费计提金额([\d\W]+)元',s):
        mf2=re.search('资产支持证券管理人的管理费计提金额([\d\W]+)元',s).group(1)
    elif re.search('资产支持专项计划管理人计提管理费([\d\W]+)元',s):
        mf2=re.search('资产支持专项计划管理人计提管理费([\d\W]+)元',s).group(1)
    elif re.search('报告期内发生应支付资产支持计划管理人的管理费([\d\W]+)元',s):
        mf2=re.search('报告期内发生应支付资产支持计划管理人的管理费([\d\W]+)元',s).group(1)
    else:
        mf2=''
    return mf2

# 基金托管人托管费
def get_cf1(s):
    cf1=re.search('基金托管人(?:计提)?托管费为?([\d\W]+)元',s)
    if cf1:
        return cf1.group(1)
    elif re.search('基金托管人的托管费计提金额([\d\W]+)元',s):
        cf1=re.search('基金托管人的托管费计提金额([\d\W]+)元',s).group(1)
    elif re.search('基金层面托管费([\d\W]+)元',s):
        cf1=re.search('基金层面托管费([\d\W]+)元',s).group(1)
    elif re.search('报告期内发生应支付基金托管人的托管费共计([\d\W]+)元',s):
        cf1=re.search('报告期内发生应支付基金托管人的托管费共计([\d\W]+)元',s).group(1)
    else:
        cf1=''
    return cf1

# 资产支持证券托管人托管费
def get_cf2(s):
    cf2=re.search('资产支持证券托管人托管费([\d\W]+)元',s)
    if cf2:
        return cf2.group(1)
    elif re.search('资产支持专项计划计提托管费([\d\W]+)元',s):
        cf2=re.search('资产支持专项计划计提托管费([\d\W]+)元',s).group(1)
    elif re.search('资产支持专项计划层面托管费([\d\W]+)元',s):
        cf2=re.search('资产支持专项计划层面托管费([\d\W]+)元',s).group(1)
    else:
        cf2=''
    return cf2

# 外部机构计提管理费
def get_mf3(s):
    mf3=re.search('(外部|运营)管理机构(?:计提)?管理费([\d\W]+)元',s)
    if mf3:
        return mf3.group(2)
    elif re.search('外部管理机构的管理费.*?计提金额([\d\W]+)元',s):
        mf3=re.search('外部管理机构的管理费.*?计提金额([\d\W]+)元',s).group(1)
    elif re.search('运营(服务费用|管理费)为?([\d\W]+)元',s):
        mf3=re.search('运营(服务费用|管理费)为?([\d\W]+)元',s).group(2)
    elif re.search('报告期内发生应支付运营管理机构的管理费([\d\W]+)元',s):
        mf3=re.search('报告期内发生应支付运营管理机构的管理费([\d\W]+)元',s).group(1)
    else:
        mf3=''
    return mf3

# temp='''
# 3.4.1基金管理人的管理费（1）固定管理费基金收取的固定管理费计算方法如下：基金当年固定管理费为前一估值日基金资产净值的 0.1%年费率与基金当年可供分配金额的7%之和，按年收取。其中，固定管理费与基金资产净值挂钩部分按日计提、按年收取。如无前一估值日的，以基金募集净金额作为计费基础。公式如下：H＝E×0.1%÷当年天数H为按日应计提的与基金资产净值挂钩的基金固定管理费E为前一估值日基金资产净值（或基金募集净金额）本报告期与净值相关的固定管理费计提 762,476.00 元，尚未划付；与年度可供分配金额相关的固定管理费计提 12,093,329.22 元，尚未划付。此部分固定管理费含向资产支持证券管理人支付的资产支持证券管理人管理费。（2）浮动管理费基金收取的浮动管理费计算方法如下：基金收取的浮动管理费=年度基金可供分配金额超出 1.4亿元部分×10%+项目公司年度运营收入超过395,153,982.54元部分×20%。浮动管理费基金管理人按年一次性收取。基金管理人与基金托管人双方核对无误后，基金托管人按照与基金管理人协商一致的方式从基金财产中一次性支付给管理人。 若遇法定节假日、公休假等，支付日期顺延。本报告期内，基金管理人根据年度可供分配现金及项目公司年度运营收入计提全年浮动管理费9,186,695.05元，尚未划付。此部分浮动管理费含向外部管理机构支付的外部机构管理费。3.4.2基金托管人的托管费基金托管人收取的基金托管费计算方法如下：本基金的托管费按前一估值日资产净值的0.05%年费率计提。托管费的计算方法如下：H＝E×0.05%÷当年天数H为按日应计提的基金托管费E为前一估值日基金资产净值（或基金募集净金额）如无前一估值日的，以基金募集净金额作为计费基础。基金托管费按日计提，按年支付。基金管理人与基金托管人双方核对无误后，基金托管人按照与基金管理人协商一致的方式从基金财产中一次性支取。若遇法定节假日、公休假等，支付日期顺延。本报告期内，计提托管费381,239.04元，尚未划付。3.4.3 资产支持证券管理人管理费资产支持证券管理人管理费计算方法如下：资产支持证券管理人每个计费周期的管理费=专项计划设立日的资产支持证券规模×0.1%×专项计划在该计费周期内实际存续天数/365。管理费按年收取。每年结束后，在提取“中航首钢生物质封闭式基础设施证券投资基金管理费”后，基金管理人按照上述计算方式核算资产支持证券管理费用，在核算完毕后的5个工作日内一次性支付给资产支持证券管理人。将由基金管理人统一收取基金管理费后进行划付。本报告期计提758,742.90元，尚未划付。3.4.4外部管理机构管理费外部管理机构管理费计算方法如下：（任期内自然年度项目公司的实际收入-收入基数）×20%，由基金管理人统一收取基金浮动管理费后支付。外部管理机构本报告期内应获得管理费5,910,510.45元，尚未划付。
# '''

def process_180801(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    a=re.findall('与净值相关的固定管理费计提([\d\W]+)元',s)[0]
    b=re.findall('与年度.*相关的固定管理费计提([\d\W]+)元',s)[0]
    c=re.findall('计提全年浮动管理费([\d\W]+)元',s)[0]
    mf1=float(a.replace(',',''))+float(b.replace(',',''))+float(c.replace(',',''))
    mf2=re.findall('资产支持证券管理人.*计提([\d\W]+)元',s)[0]
    cf1=re.findall('计提托管费([\d\W]+)元',s)[0]
    mf3_sum=re.findall('外部管理机构管理费.*管理费([\d\W]+)元',s)[0]
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_180102(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    a=re.findall('外部管理机构浮动管理费\s?A\s?([\d\W]+)元',s)[0]
    b=re.findall('浮动管理费\s?B\s?([\d\W]+)元',s)[0]
    mf3_variable=float(a.replace(',',''))+float(b.replace(',',''))
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_180103(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    mf3_fixed=re.findall('外部管理机构基础服务报酬([\d\W]+)元',s)[0]
    mf3_variable=re.findall('浮动服务报酬([\d\W]+)元',s)[0]
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_180202(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    cf2=get_cf2(s)
    try:
        mf3_sum=get_mf3(s)
    except:
        pass
    try:
        mf3_variable=re.findall('(?:运营管理机构收取的)?浮动管理费([\d\W]+)元',s)[0]
    except:
        pass
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_180301(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    mf3_variable=re.findall('报告期内发生应支付外部管理机构的浮动管理费(?:共计)?([\d\W]+)元',s)[0]
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values


def process_180401(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf12=re.findall('基金管理人与.*计划管理人计提管理费合计([\d\W]+)元',s)[0]
    cf1=get_cf1(s)
    try :
        mf3_fixed=re.findall('外部管理机构(?!预提).*?固定管理费为?([\d\.,]+).*?元',s)[0]  ##不出现预提两个字才匹配成功
    except:
        pass
    try:
        mf3_variable=re.findall('外部管理机构(?!预提).*?浮动管理费为([\d\W]+)元',s)[0]  #只有年报里有
    except:
        pass
    try:
        mf3_sum=re.findall('外部管理机构(?!预提).*?全年管理费([\d\W]+)元',s)[0]  #只有年报里有
    except:
        pass
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_180501(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    mf3_fixed = re.findall('运营管理机构.*固定管理费为?([\d\W]+)元',s)[0]
    if re.findall('运营管理机构.*浮动管理费为?([\d\W]+)元',s):
        mf3_variable=re.findall('运营管理机构.*浮动管理费为?([\d\W]+)元',s)[0]
        mf3_sum=float(mf3_fixed.replace(',',''))+float(mf3_variable.replace(',',''))
    elif re.search('报告期内未发生应支付运营管理机构的浮动管理费',s):
        mf3_variable=0
        mf3_sum=float(mf3_fixed.replace(',',''))+mf3_variable
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values


def process_508000(s):  # 华安
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=re.findall('基金管理人.*计提的?管理费为?([\d\W]+)元.*资产支持证券管理人',s)[0]
    mf2=re.findall('资产支持证券管理人.*计提的?管理费为?([\d\W]+)元',s)[0]
    cf1=re.findall('托管人.*计提的?托管费为?([\d\W]+)元',s)[0]
    try:
        mf3_fixed=re.findall('外部管理机构.*计提的固定管理费为([\d\W]+)元',s)[0]
    except:
        mf3_fixed=''
    try:
        mf3_variable=re.findall('外部管理机构.*计提的浮动管理费为([\d\W]+)元',s)[0]
    except:
        mf3_variable=''
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508008(s):   # 国金
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf_sum=re.findall('计提基金及.*计划托管人托管费合计([\d\W]+)元',s)[0]
    mf3_variable=re.findall('外部管理机构.*计提浮动管理费([\d\W]+)元',s)[0]
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508028(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    a=re.findall('计提的基金管理人的固定管理费1为([\d\W]+)元',s)[0]
    b=re.findall('计提的基金管理人的固定管理费2为([\d\W]+)元',s)[0]
    mf1=float(a.replace(',',''))+float(b.replace(',',''))
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508077(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=get_mf1(s)
    mf2=get_mf2(s)
    cf1=get_cf1(s)
    mf3_variable=re.findall('浮动管理费为?([\d\W]+)元',s)[0]  # 根据收费规则浮动100%都是外部管理机构的
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508088(s):   # 508021  都是国泰君安
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=re.findall('基金管理人.*计提的?管理费为?([\d\W]+)元',s)[0]
    cf1=re.findall('托管人.*计提的?托管费为?([\d\W]+)元',s)[0]
    mf3_sum=re.findall('外部管理机构.*计提.*?运营管理费([\d\W]+)元，',s)[0]
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508096(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    if re.findall('固定管理费包括基金管理人和资产支持证券管理人的管理费',s):
        c=re.findall('本报告期计提固定管理费([\d\W]+)元',s)[0]
        mf2=re.findall('其中资产支持证券管理人的管理费([\d\W]+)元',s)[0]
        mf1=float(c.replace(',',''))-float(mf2.replace(',',''))

    cf1=re.findall('基金托管人.*?本报告期计提托管费为?([\d\W]+)元',s)[0]
    a= re.findall('计提外部管理机构运营管理成本及运营管理服务费([\d\W]+)元',s)[0]
    b= re.findall('计提外部管理机构运营管理成本及运营管理服务费([\d\W]+)元',s)[1]
    mf3_sum=float(a.replace(',',''))+float(b.replace(',',''))
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508001(s):   # 浙商
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    a=re.findall('基金管理人的固定管理费.*计提固定管理费([\d\W]+)元',s)[0]
    b=re.findall('基金管理人的浮动管理费为?([\d\W]+)元',s)[0]
    mf1=float(a.replace(',',''))+float(b.replace(',',''))
    cf1=re.findall('基金托管人的托管费.*计提托管费([\d\W]+)元',s)[0]
    try:
        mf3_sum=re.findall('按权责发生制实际发生的运营管理成本为([\d\W]+)元',s)[0]
    except:
        pass
    if re.search('本基金无资产支持证券管理人管理费及资产支持证券托管人托管费',s):
        mf2=cf2=0
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

def process_508006(s):
    mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
    mf1=re.findall('基金管理人费用收取情况.*发生费用金额([\d\W]+)元',s)[0]
    cf1=re.findall('基金层面托管费([\d\W]+)元',s)[0]
    cf2=re.findall('资产支持专项计划层面托管费([\d\W]+)元',s)[0]
    a=re.findall('基础服务费\s?A\s?为([\d\W]+)元',s)[0]
    b=re.findall('基础服务费\s?B\s?为([\d\W]+)元',s)[0]
    mf3_fixed=float(a.replace(',','').replace('，',''))+float(b.replace(',',''))
    try:
        mf3_variable=re.search('浮动(管理|服务)费([\d\W]+)元。$',s).group(2)  #这一项年报有，中期没有
    except:
        pass
    values=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return values

# print(temp)
# process_180801('180801',temp)
# print(get_mf1(temp))
# print(get_mf2(temp))
# print(get_cf1(temp))
# print(get_cf2(temp))
# print(get_mf3(temp))

# %%
def get_data(code,content):
    code_mapping = {
        '180801': process_180801,
        '180102': process_180102,
        '180103': process_180103,
        '180202': process_180202,
        '180301': process_180301,
        '180401': process_180401,
        '180501': process_180501,
        '508000': process_508000,
        '508008': process_508008,
        '508021': process_508088, #508021和508088都是国泰君安
        '508077': process_508077,
        '508088': process_508088,
        '508001': process_508001,
        '508006': process_508006,
        '508028': process_508028,
        '508096': process_508096,
    }
    if code in code_mapping.keys():
        result = code_mapping[code](content)
    else:
        mf1=mf2=mf12=cf1=cf2=cf12=mf3_fixed=mf3_variable=mf3_sum=''
        mf1=get_mf1(content)
        mf2=get_mf2(content)
        cf1=get_cf1(content)
        cf2=get_cf2(content)
        mf3_sum=get_mf3(content)
        result=[mf1,mf2,mf12,cf1,cf2,cf12,mf3_fixed,mf3_variable,mf3_sum]
    return result

# if __name__ == '__main__':
    # root_dir = 'PDF'
    # main(root_dir)
    # main(r'.\Qreport_PDF')
    
