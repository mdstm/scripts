'''使用 cmake 配置并构建项目'''

import argparse
import os


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('-s', '--source', default='.', help='源路径')
    p.add_argument('-b', '--build', default='build', help='构建路径')
    p.add_argument('-r', '--release', action='store_true', help='发行版')
    p.add_argument('other', nargs='*', help='其他 cmake 参数')
    p.add_argument('-c', '--clean', action='store_true', help='删除原构建')

    args = p.parse_args()

    build = args.build

    if args.clean and os.path.exists(build):
        from shutil import rmtree
        rmtree(build)

    cmd = f'cmake -G Ninja -S "{args.source}" -B "{build}"'\
        ' -DCMAKE_INSTALL_PREFIX=install'\
        ' -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++'\
        ' -DCMAKE_EXPORT_COMPILE_COMMANDS=ON'\
        f' -DCMAKE_BUILD_TYPE={(
            'Release' if args.release else
            'Debug -DCMAKE_VERBOSE_MAKEFILE=ON'
        )}'

    if (other := args.other):
        cmd += '" "'.join(other).join((' "', '"'))

    cmd += f' && cmake --build "{build}"'

    print(cmd)
    os.system(cmd)


if __name__ == '__main__':
    main()
