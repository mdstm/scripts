'''给文件名按顺序编号'''

import argparse
import os
import re


split = re.compile(r'\d+|[^\d]+').findall # 将数字和非数字分割开

def add_key(name: str) -> tuple[str, tuple]:
    '''给文件名添加用于排序的 key'''
    key = split('a' + name.lower()) # 添加前缀，确保第一项为非数字
    key[0] = key[0][1:]
    for i in range(1, len(key), 2): # 将所有数字字符串转换为整型
        key[i] = int(key[i])
    return name, key


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('first', nargs='?', type=int, default=0, help='编号初始值')
    p.add_argument('length', nargs='?', type=int, default=0, help='编号长度')

    args = p.parse_args()

    names = next(os.walk('.'))[2]
    first = max(0, args.first)
    length = max(len(str(first + len(names) - 1)), args.length)
    format = str(length).join(('{:0', 'd}{}')).format

    names = sorted(map(add_key, names), key=lambda x: x[1])
    for i, (name, _) in enumerate(names, first):
        ext = name[p:] if (p := name.rfind('.')) != -1 else ''
        name_ = format(i, ext)
        if name != name_:
            os.rename(name, name_)
            print(f'{name} -> {name_}')


if __name__ == '__main__':
    main()
