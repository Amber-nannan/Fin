# -*- coding: UTF-8 –*-

import pdf_to_excel_quarterly
import pdf_to_excel_annual
import pdf_to_excel_mid
import szse_download
import sse_download
# import C_REITs.Fin_rp.copy_xlsx as copy_xlsx

import datetime
from pathlib import Path
import shutil
import os
import re

# 注意和copy_xlsx.py中的main函数区分
# 把root_dir中不含Mgmt的.xlsx文件copy到save_dir中
def copy_xlsx(root_dir, save_dir):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_directory, root_dir)
    save_dir = os.path.join(current_directory, save_dir)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f'创建文件夹 - {save_dir}')

    for file in Path(root_dir).rglob('*.xlsx'):
        savepath = Path(save_dir).joinpath(file.name)
        if not bool(re.search('Mgmt', file.name)):
            # if savepath.exists():
            #     continue
            shutil.copy(file, savepath)
            print(savepath, '保存成功')

def copy_mgt_fee(root_dir):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_directory, root_dir)
    save_dir = os.path.join(current_directory, 'mgt_fee')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f'创建文件夹 - {save_dir}')
    if 'Q' in root_dir:
        subfolder='Quarterly_mgt_fee'
    elif 'A' in root_dir:
        subfolder='Annual_mgt_fee'
    else:
        subfolder='Midterm_mgt_fee'

    for file in Path(root_dir).rglob('*Mgmt.xlsx'):
        mgt_subfolder=Path(save_dir).joinpath(subfolder)
        if not os.path.exists(mgt_subfolder):
            os.makedirs(mgt_subfolder)
            print(f'创建文件夹 - {subfolder}')
        savepath = Path(save_dir).joinpath(subfolder,file.name)
        shutil.copy(file, savepath)
        print(savepath, '保存成功')

# %%
def download_creits_pdf():
    startDate = '2021-06-21'
    endDate = datetime.datetime.today().strftime('%Y-%m-%d')
    sse_download.main(startDate, endDate)  # # 上海证券交易所pdf下载
    szse_download.main(startDate, endDate)  # 深圳证券交易所pdf下载


def read_creits_pdf_data(update):
    pdf_to_excel_quarterly.main('Qreport_PDF', update)  # pdf提取到excel
    pdf_to_excel_annual.main('Areport_PDF', update)  # pdf提取到excel
    pdf_to_excel_mid.main('Midreport_PDF', update)  # pdf提取到excel


def downloada_and_read_creits_pdf_data(download,update):
    if download:
        download_creits_pdf()
    read_creits_pdf_data(update)
    copy_xlsx('Qreport_PDF', 'Quarterly_report')   # 把诸如2023Q1.xlsx复制到Quarterly_report文件夹中
    copy_xlsx('Areport_PDF', 'Annual_report')  
    copy_xlsx('Midreport_PDF', 'Midterm_report')   
    copy_mgt_fee('Qreport_PDF')  # 把诸如mgmt.xlsx复制到mgt_fee文件夹中
    copy_mgt_fee('Areport_PDF')
    copy_mgt_fee('Midreport_PDF')

    print('=' * 50)
    print('PDF下载及提取至文件夹已经全部完成')
    print('=' * 50)

downloada_and_read_creits_pdf_data(True,'part')

