# -*- coding: UTF-8 –*-
import json
import re
import time
from pathlib import Path
import requests
import random

# 上海证券交易所pdf下载

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'http://www.sse.com.cn/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}

han_item = {'一':1,'二':2,'三':3,'四':4,
            '二0二四':2024,'二0二三':2023,'二0二二':2022,'二0二一':2021}

def get_pdf(filepath,pdf_url):
    res = requests.get(pdf_url,headers)
    with open(filepath,'wb') as f:
        f.write(res.content)
    print(filepath,'保存成功。')


# 与深交所不同，上交所没有关键词搜索，所以需要在结果里遍历，判断是否是年报或季报
def get_page(startDate,endDate,quarterly_root_dir,annual_root_dir):
    rand_=random.randint(10**5, 10**6)
    params = {
        'jsonCallBack': f'jsonpCallback{rand_}',
        'sqlId': 'REITS_BULLETIN',
        'isPagination': 'true',
        'fundCode': '',
        'startDate': startDate,
        'endDate': endDate,
        'pageHelp.pageSize': '1000',
        'pageHelp.cacheSize': '1',
        'pageHelp.pageNo': '1',
        'pageHelp.beginPage': '1',
        'pageHelp.endPage': '5',
        '_': int(time.time()*1000),
    }
    url='http://query.sse.com.cn/commonSoaQuery.do'
    response = requests.get(url=url, params=params, headers=headers, verify=False)
    data = re.findall('jsonpCallback\d+\((.*?)\)$',response.text)[0]
    js_data = json.loads(data)
    pageCount = js_data['pageHelp']['pageCount']//25+1
    for pageNo in range(pageCount):
        params['pageHelp.pageNo'] = pageNo + 1
        response = requests.get(url=url, params=params, headers=headers, verify=False)
        data = re.findall('jsonpCallback\d+\((.*?)\)$',response.text)[0]
        js_data = json.loads(data)
        dataList = js_data['pageHelp']['data']
        for data in dataList:
            title = data['title']
            code = data['securityCode']
            pdf_url = "http://www.sse.com.cn" +data['url']
            if re.search('年度?第\w季度报告$',title) :
                year,jd = re.findall('(\w{4})年度?第(\w{1})季度报告$',title)[0]
                jd = han_item[jd] if jd in han_item else jd
                year = han_item[year] if year in han_item else year        
                base_dir = Path(quarterly_root_dir).joinpath(f"{year}Q{jd}").joinpath('Q_report')
                filename = f"{code}_{year}Q{jd}.pdf"
                filepath = base_dir.joinpath(filename)
                if not base_dir.exists():
                    base_dir.mkdir(parents=True,exist_ok=True)
                if not filepath.exists():
                    get_pdf(str(filepath),pdf_url)
                else:
                    print(filepath,'已存在。')

            elif re.search('年度报告$',title):
                year =re.findall('(\d{4})年年度报告$',title)[0]  # 测试正则表达式
                base_dir = Path(annual_root_dir).joinpath(f"{year}A").joinpath('A_report')
                filename = f"{code}_{year}A.pdf"
                filepath = base_dir.joinpath(filename)
                if not base_dir.exists():
                    base_dir.mkdir(parents=True,exist_ok=True)
                if not filepath.exists():
                    get_pdf(str(filepath),pdf_url)
                else:
                    print(filepath,'已存在。')

def main(startDate,endDate):
    get_page(startDate,endDate,'Qreport_PDF','Areport_PDF')


# 上海证券交易所pdf下载

# if __name__ == '__main__':
#     startDate = '2021-06-01'
#     endDate = '2023-05-01'
#     root_dir = 'Qreport_PDF'
#     main(startDate, endDate, root_dir)