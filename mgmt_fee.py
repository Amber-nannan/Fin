import re
from pathlib import Path
import pdfplumber
import pandas as pd
# 基金管理人计提管理费
def get_mf1(s):
    mf1=re.search('计提基金管理人管理费([\d\W]+)元',s)
    if mf1:
        return mf1.group(1)
    elif re.search('基金管理人的管理费计提金额([\d\W]+)元',s):
        mf1=re.search('基金管理人的管理费计提金额([\d\W]+)元',s).group(1)
    elif re.search('基金管理人计提管理费([\d\W]+)元',s):
        mf1=re.search('基金管理人计提管理费([\d\W]+)元',s).group(1)
    elif re.search('基金管理人(?:收取)?的?管理费为?([\d\W]+)元',s):
        mf1=re.search('基金管理人(?:收取)?的?管理费为?([\d\W]+)元',s).group(1)
    else:
        mf1=''
    return mf1

# 资产支持证券管理人管理费
def get_mf2(s):
    mf2=re.search('资产支持证券管理人(?:收取)?的?管理费为?([\d\W]+)元',s)
    if mf2:
        return mf2.group(1)
    elif re.search('资产支持证券管理人的管理费计提金额([\d\W]+)元',s):
        mf2=re.search('资产支持证券管理人的管理费计提金额([\d\W]+)元',s).group(1)
    elif re.search('资产支持专项计划管理人计提管理费([\d\W]+)元',s):
        mf2=re.search('资产支持专项计划管理人计提管理费([\d\W]+)元',s).group(1)
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

# 一个pdf返回一个字典，包含各管理费
def get_data(file):
    pdf = pdfplumber.open(file)
    code=file[-17:-11]
    code= code+'.SH' if code[0]==5 else code+'.SZ'
    content = ''
    for page in pdf.pages:
        text = page.extract_text()
        content += text
    lines = content.splitlines()
    a = 0
    b = 0
    content = ''
    for line in lines:
        if '6.2' in line and '基金费用' in line and '收取情况' in line:
            a = lines.index(line)
        if '6.3' in line and '管理人' in line:
            b = lines.index(line)
            break
    if b > a:
        fuck = lines[a+1:b]
        content = ''.join(fuck)
        mf1=get_mf1(content)
        mf2=get_mf2(content)
        cf1=get_cf1(content)
        cf2=get_cf2(content)
        #cf3=get_cf3(content)
        remarks=content
        # content = re.sub('\s+','',content)
        data = {'代码':code,'基金管理人计提管理费': mf1,'计划管理人计提管理费': mf2,'基金托管人计提托管费': cf1,
        '计划管理人计提托管费':cf2,'外部管理机构计提管理费':'','remarks':remarks}
    return data

# 一个季度返回一个excel
def run(base_dir,name):
    df=pd.DataFrame({'代码':[],'基金管理人计提管理费': [],'计划管理人计提管理费': [],'基金托管人计提托管费': [],
            '计划管理人计提托管费':[],'外部管理机构计提管理费':[],'remarks':[]})
    for file in Path(base_dir).glob('**/*.pdf'):
        print(file,'开始提取。')
        try:
            new_data = get_data(str(file))
            df.loc[df.shape[0]]=new_data
        except Exception as e:
            print(e)
    df.to_excel(name,encoding='utf-8',index=False)

# 所有季度
def main(root_dir):
    for base_dir in Path(root_dir).glob('*'):
        if base_dir.is_dir():
            name = base_dir.joinpath(base_dir.stem +'管理费.xlsx')
            if name.exists():
                print(name,'已存在')
            else:
                run(base_dir,name)
                print(name,'保存成功。')


# 后面反正就是在R2这个格子后面可以加：基金管理人计提管理费、计划管理人计提管理费、托管费（托管费有些没有分别披露可以合并），外部管理机构计提管理费
if __name__ == '__main__':
    # root_dir = 'PDF'
    # main(root_dir)
    main(r'.\Qreport_PDF')
    
    