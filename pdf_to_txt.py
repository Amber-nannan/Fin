import re
from pathlib import Path
import pdfplumber


# 提取基金管理人计提管理费部分，保存txt

def get_data(file):

    pdf = pdfplumber.open(file)
    content = ''
    for page in pdf.pages:
        text = page.extract_text()
        content += text
    lines = content.splitlines()
    a = 0
    b = 0
    content = ''
    for line in lines:
        if '6.2 ' in line and '基金费用' in line and '收取情况' in line:
            a = lines.index(line)
        if '6.3 ' in line and '管理人' in line:
            b = lines.index(line)
            break
    if b > a:
        fuck = lines[a+1:b]
        content = ''.join(fuck)
        # 基金管理人计提管理费
        content = re.sub('\s+','',content)
        # content = content.replace('，','')
    return content


def run(base_dir,name):
    fr = open(name,'w',encoding='utf-8')

    for file in Path(base_dir).glob('**/*.pdf'):
        print(file,'开始提取。')
        fr.write(str(file) + '\n')
        try:
            content = get_data(str(file))
            fr.write(content+'\n')
        except Exception as e:
            print(e)
        fr.write('\n')

def main(root_dir):
    for base_dir in Path(root_dir).glob('*'):
        if base_dir.is_dir():
            name = base_dir.joinpath(base_dir.stem +'.txt')
            if name.exists():
                print(name,'已存在')
            else:
                run(base_dir,name)
                print(name,'保存成功。')


# 后面反正就是在R2这个格子后面可以加：基金管理人计提管理费、计划管理人计提管理费、托管费（托管费有些没有分别披露可以合并），外部管理机构计提管理费
# if __name__ == '__main__':
#     root_dir = 'PDF'
#     main(root_dir)