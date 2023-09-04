# -*- coding: UTF-8 –*-

import pdf_to_txt
import pdf_to_excel
import reits_spider
import sse_spdier
# import C_REITs.Fin_rp.copy_xlsx as copy_xlsx


import datetime
from pathlib import Path
import shutil
import os
import re

# 注意和copy_xlsx.py中的main函数区分
# 把root_dir中不含model的.xlsx文件copy到save_dir中
def copy_xlsx(root_dir, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f'创建文件夹 - {save_dir}')

    for file in Path(root_dir).rglob('*.xlsx'):
        savepath = Path(save_dir).joinpath(file.name)
        if not bool(re.search('models', file.name)):
            # if savepath.exists():
            #     continue
            shutil.copy(file, savepath)
            print(savepath, '保存成功')


def download_creits_pdf(root_dir):
    startDate = '2021-06-21'
    endDate = datetime.datetime.today().strftime('%Y-%m-%d')
    # endDate = datetime.datetime.today()
    # root_dir = 'PDF'
    # save_dir = ''
    sse_spdier.main(startDate, endDate, root_dir)  # # 上海证券交易所pdf下载
    reits_spider.main(startDate, endDate, root_dir)  # 深圳证券交易所pdf下载


def read_creits_pdf_data(root_dir, update):
    pdf_to_excel.main(root_dir, update)  # pdf提取到excel
    pdf_to_txt.main(root_dir)  # pdf提取到txt
    # copy_xlsx(root_dir,save_dir)


def downloada_and_read_creits_pdf_data(download,update):
    root_dir = 'Qreport_PDF'
    save_dir = 'Quarterly_report'
    
    if download ==True:
        download_creits_pdf(root_dir)
    read_creits_pdf_data(root_dir, update)
    # print('目前仅在文档中更新了最新的excel，仍然需要检查数字')
    copy_xlsx(root_dir, save_dir)   # 把诸如2023Q1.xlsx复制到Quarterly_report文件夹中

    print('=' * 50)
    print('PDF下载及提取至文件夹已经全部完成')
    print('=' * 50)





