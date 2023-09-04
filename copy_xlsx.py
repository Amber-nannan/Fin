# -*- coding: utf-8 -*-
"""
Created on Fri May 19 21:37:15 2023

@author: Xu Chong
"""

from pathlib import Path
import shutil



def main(root_dir,save_dir):
    for file in Path(root_dir).rglob('*.xlsx'):
        savepath = Path(save_dir).joinpath(file.name)
        if savepath.exists():
            continue
        shutil.copy(file,savepath)
        print(savepath,'保存成功')


if __name__ == '__main__':
    root_dir = 'PDF'
    save_dir = '.'
    main(root_dir, save_dir)