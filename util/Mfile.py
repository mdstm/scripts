'''文件处理相关函数'''

import re


def normalizeName(name: str) -> str:
    r'''
    规范化文件名称，将特殊字符 \\/:*?"<>| 以及不可编码为 gbk 的字符如 ・♪
    等转换为空格，并去除多余空格
    '''

    # 将不可编码字符替换为问号
    name = name.encode('gbk', errors='replace').decode('gbk')

    # 将特殊字符替换为空格
    name = re.sub(r'[\s\\/:*?"<>|]+', ' ', name).strip()

    return name
