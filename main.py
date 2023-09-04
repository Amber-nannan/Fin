# -*- coding: UTF-8 –*-

import Fin_rp.pdf_to_txt as pdf_to_txt
import Fin_rp.pdf_to_excel as pdf_to_excel
import Fin_rp.reits_spider as reits_spider
import Fin_rp.sse_spdier as sse_spdier
# import C_REITs.Fin_rp.copy_xlsx as copy_xlsx


import datetime
from pathlib import Path
import shutil
import os
import re


def copy_xlsx(root_dir, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print('创建文件夹 - %s' % save_dir)

    for file in Path(root_dir).rglob('*.xlsx'):
        savepath = Path(save_dir).joinpath(file.name)
        if not bool(re.search('models', file.name)):
            # if savepath.exists():
            #     continue
            shutil.copy(file, save_dir)
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
    root_dir = 'Fin_rp/Qreport_PDF'
    save_dir = 'Fin_rp/Quarterly_report'
    
    if download ==True:
        download_creits_pdf(root_dir)
    shutil.copy('Fin_rp/models1.xlsx', root_dir)
    read_creits_pdf_data(root_dir, update)
    # print('目前仅在文档中更新了最新的excel，仍然需要检查数字')
    copy_xlsx(root_dir, save_dir)

    print('=' * 50)
    print('PDF下载及提取至文件夹已经全部完成')
    print('=' * 50)





