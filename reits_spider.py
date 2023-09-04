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
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'http://reits.szse.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://reits.szse.cn/disclosure/index.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'X-Request-Type': 'ajax',
    'X-Requested-With': 'XMLHttpRequest',
}


han_item = {'一':1,'二':2,'三':3,'四':4,
            '二0二四':2024,'二0二三':2023,'二0二二':2022,'二0二一':2021}

def get_pdf(filepath,pdf_url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'http://reits.szse.cn/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }
    res = requests.get(pdf_url,headers,verify=False,)
    # print(res.headers)
    with open(filepath,'wb') as f:
        f.write(res.content)
    print(filepath,'保存成功。')




def get_page(page,startDate,endDate,root_dir):
    params = {
        'random': random.random(),
    }

    json_data = {
        'seDate': [
            startDate,
            endDate,
        ],
        'searchKey': [
            '季度报告',
        ],
        'channelCode': [
            'reits-xxpl',
        ],
        'bigCategoryId': [
            'quarterreport',
        ],
        'pageSize': 100,
        'pageNum': page,
    }
    response = requests.post(
        'http://reits.szse.cn/api/disc/announcement/annList',
        params=params,
        headers=headers,
        json=json_data,
        verify=False,
    )

    data = response.json()['data']
    announceCount = response.json()['announceCount']
    for d in data:
        title = d['title']
        code = d['secCode'][0]
        pdf_url ="http://reits.szse.cn/api/disc/info/download?id={}".format(d['id'])
        if re.search('年第\w季度报告$',title) or re.search('年\w季度报告$',title):
            if re.search('年第\w季度报告$',title):
                year,jd = re.findall('(\w{4})年第(\w{1})季度报告$',title)[0]
            
            if re.search('年\w季度报告$',title):
                year,jd = re.findall('(\w{4})年(\w{1})季度报告$',title)[0]

            if jd in han_item:
                jd = han_item.get(jd)
            if year in han_item:
                year = han_item.get(year)
            base_dir = Path(root_dir).joinpath(f"{year}Q{jd}").joinpath('Q_report')
            if not base_dir.exists():
                base_dir.mkdir(parents=True,exist_ok=True)

            filename = f"{code}_{year}Q{jd}.pdf"
            filepath = base_dir.joinpath(filename)
            if not filepath.exists():
                get_pdf(str(filepath),pdf_url)
            else:
                print(filepath,'已存在。')

    return math.ceil(announceCount/50)

def main(startDate,endDate,root_dir):
    page = 1
    while 1:
        print('开始爬取页数>>>>>',page)
        total_page = get_page(page,startDate,endDate,root_dir)
        page +=1
        time.sleep(3)
        if page > total_page:
            break


# 深圳证券交易所pdf下载

# if __name__ == '__main__':
#     startDate = '2021-06-01'
#     endDate = '2023-05-01'
#     root_dir = 'Qreport_PDF'
#     main(startDate,endDate,root_dir)
