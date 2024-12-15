'''计算文件的 hash 值'''

import argparse
from hashlib import file_digest, algorithms_available


def main():
    p = argparse.ArgumentParser(description=__doc__,
        epilog='可用的 hash 算法有: ' + ', '.join(algorithms_available),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('file', nargs='+', help='文件名称')
    p.add_argument('-a', '--algorithm', default='sha256', help='hash 算法')

    args = p.parse_args()

    algo = args.algorithm
    for name in args.file:
        with open(name, 'rb') as f:
            print(file_digest(f, algo).hexdigest())


if __name__ == '__main__':
    main()
