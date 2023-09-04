# -*- coding: UTF-8 –*-
import json
import re
import time
from pathlib import Path
import requests


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




def get_page(page,startDate,endDate,root_dir):

    params = {
        'jsonCallBack': 'jsonpCallback79355',
        'sqlId': 'REITS_BULLETIN',
        'isPagination': 'true',
        'fundCode': '',
        'startDate': startDate,
        'endDate': endDate,
        'pageHelp.pageSize': '1000',
        'pageHelp.cacheSize': '1',
        'pageHelp.pageNo': page,
        'pageHelp.beginPage': page,
        'pageHelp.endPage': '5',
        '_': int(time.time()*1000),
    }

    response = requests.get('http://query.sse.com.cn/commonSoaQuery.do', params=params, headers=headers, verify=False)
    data = re.findall('jsonpCallback\d+\((.*?)\)$',response.text)[0]
    js_data = json.loads(data)
    total_page = js_data['pageHelp']['pageCount']
    for d in js_data['result']:
        title = d['title']
        if re.search('年第\w季度报告$',title) or re.search('年度第\w季度报告$',title) :
            if re.search('年第\w季度报告$',title):
                year,jd = re.findall('(\w{4})年第(\w{1})季度报告$',title)[0]
            if re.search('年度第\w季度报告$',title):
                year,jd = re.findall('(\w{4})年度第(\w{1})季度报告$',title)[0]
            if jd in han_item:
                jd = han_item.get(jd)
            if year in han_item:
                year = han_item.get(year)

            code = d['securityCode']
            pdf_url = "http://www.sse.com.cn" +d['url']
            base_dir = Path(root_dir).joinpath(f"{year}Q{jd}").joinpath('Q_report')
            if not base_dir.exists():
                base_dir.mkdir(parents=True,exist_ok=True)

            filename = f"{code}_{year}Q{jd}.pdf"
            filepath = base_dir.joinpath(filename)
            if not filepath.exists():
                get_pdf(str(filepath),pdf_url)
            else:
                print(filepath,'已存在。')
    return total_page


def main(startDate,endDate,root_dir):
    page = 1
    while 1:
        print('开始爬取页数>>>>>',page)
        total_page = get_page(page,startDate,endDate,root_dir)
        page +=1
        time.sleep(3)
        if page > total_page:
            break


# 上海证券交易所pdf下载

# if __name__ == '__main__':
#     startDate = '2021-06-01'
#     endDate = '2023-05-01'
#     root_dir = 'Qreport_PDF'
#     main(startDate, endDate, root_dir)