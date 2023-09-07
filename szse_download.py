# -*- coding: UTF-8 –*-

"""
深圳证券交易所pdf下载
"""
import math
import random
import requests
import re
import time
from pathlib import Path

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=utf-8",
    "Referer": "http://reits.szse.cn/projectdynamic/index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}


han_item = {'〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '零': 0,
            '二0二四': 2024, '二0二三': 2023, '二0二二': 2022, '二0二一': 2021,
            '二〇二四': 2024, '二〇二三': 2023, '二〇二二': 2022, '二〇二一': 2021}

def get_pdf(filepath,pdf_url):
    res = requests.get(pdf_url,headers,verify=False,)
    # print(res.headers)
    with open(filepath,'wb') as f:
        f.write(res.content)
    print(filepath,'保存成功。')

# report_type 请填写'quarterly' 或'annual'
def get_page(startDate,endDate,report_type,root_dir):
    url = 'http://reits.szse.cn/api/disc/announcement/annList'
    
    if report_type=='quarterly':
        searchKey='季度报告' 
    elif report_type=='annual':
        searchKey='年度报告' 
    else:
        searchKey='中期报告'
    params = {
        'random': random.random(),
    }
    json_data = {
        'seDate': [startDate,endDate],
        'searchKey': [searchKey],
        'channelCode': ['reits-xxpl'],
        'pageSize': 50,
        'pageNum': '1',
    }
    response = requests.post(url=url,params=params,headers=headers,json=json_data,verify=False)
    pageCount = response.json()['announceCount']//50+1
    for pageNo in range(pageCount):
        print(f'开始爬取深交所{searchKey}页数>>>>>{pageNo+1}')
        json_data['pageNum'] = str(pageNo + 1)
        response = requests.post(url, headers=headers, params=params, json=json_data, verify=False)
        dataList = response.json()['data']    

        for data in dataList:
            title = data['title']
            code = data['secCode'][0]
            pdf_url ="http://reits.szse.cn/api/disc/info/download?id={}".format(data['id'])
            if  report_type=='quarterly':
                if re.search('年第?\w季度报告$',title):
                    year,jd = re.findall('(\w{4})年度?第?(\w{1})季度报告$',title)[0]
                    jd = han_item[jd] if jd in han_item else jd
                    year = han_item[year] if year in han_item else year
                    base_dir = Path(root_dir).joinpath(f"{year}Q{jd}").joinpath('Q_report')
                    filename = f"{code}_{year}Q{jd}.pdf"
                    filepath = base_dir.joinpath(filename)
                    if not base_dir.exists():
                        base_dir.mkdir(parents=True,exist_ok=True)
                    if not filepath.exists():
                        get_pdf(str(filepath),pdf_url)
                    else:
                        print(filepath,'已存在。')

            if  report_type=='annual':       
                if re.search('年度报告$',title):
                    year =re.findall('(二0[\u4e00-\u9fa5]{2}|\d{4}|二〇[\u4e00-\u9fa5]{2})年度?', title)[0]
                    year = han_item[year] if year in han_item else year
                    base_dir = Path(root_dir).joinpath(f"{year}A").joinpath('A_report')
                    filename = f"{code}_{year}A.pdf"
                    filepath = base_dir.joinpath(filename)
                    if not base_dir.exists():
                        base_dir.mkdir(parents=True,exist_ok=True)
                    if not filepath.exists():
                        get_pdf(str(filepath),pdf_url)
                    else:
                        print(filepath,'已存在。')
            if  report_type=='mid':       
                if re.search('中期报告$',title):
                    year =re.findall('(二0[\u4e00-\u9fa5]{2}|\d{4}|二〇[\u4e00-\u9fa5]{2})年度?', title)[0]
                    year = han_item[year] if year in han_item else year
                    base_dir = Path(root_dir).joinpath(f"{year}Mid").joinpath('Mid_report')
                    filename = f"{code}_{year}Mid.pdf"
                    filepath = base_dir.joinpath(filename)
                    if not base_dir.exists():
                        base_dir.mkdir(parents=True,exist_ok=True)
                    if not filepath.exists():
                        get_pdf(str(filepath),pdf_url)
                    else:
                        print(filepath,'已存在。')

def main(startDate,endDate):
    get_page(startDate,endDate,'quarterly','Qreport_PDF')
    get_page(startDate,endDate,'annual','Areport_PDF')
    get_page(startDate,endDate,'mid','Midreport_PDF')


# main('2021-01-01','2023-09-05')

# 深圳证券交易所pdf下载

# if __name__ == '__main__':
#     startDate = '2021-06-01'
#     endDate = '2023-05-01'
#     root_dir = 'Qreport_PDF'
#     main(startDate,endDate,root_dir)
