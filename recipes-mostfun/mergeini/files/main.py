#!/usr/bin python
# coding: utf-8
import sys
from argparse import ArgumentParser

from configobj import ConfigObj
from os.path import exists


def main(*args):
    source_file = args[0].source
    target_file = args[0].target

    if check_file(source_file):
        pass
    else:
        return

    if check_file(target_file):
        pass
    else:
        return

    try:
        source_obj = ConfigObj(source_file, encoding='UTF8')
        target_obj = ConfigObj(target_file, encoding='UTF-8')

        if args[0].union:
            union(source_obj=source_obj, target_obj=target_obj)
        elif args[0].intersection:
            intersection(source_obj=source_obj, target_obj=target_obj)
        else:
            pass
            return
        target_obj.write()
    except Exception as e:
        print(e)
    else:
        pass
    finally:
        return


def analyse_ini(ini_obj):
    ini_dict = ini_obj.dict()
    section_keys = ini_dict.keys()
    return section_keys


def analyse_section(ini_section):
    item_keys = ini_section.keys()
    return item_keys


def union(source_obj, target_obj):
    source_section_keys = analyse_ini(source_obj)
    target_section_keys = analyse_ini(target_obj)
    for sk in source_section_keys:
        if sk in target_section_keys:
            # check and replace the values with the old ini
            source_item_keys = analyse_section(source_obj[sk])
            for ik in source_item_keys:
                # no matter ik is in target_obj[sk] or not, just put the value into target_obj
                target_obj[sk][ik] = source_obj[sk][ik]
        else:
            # copy the sections that in the old ini but not in the new ini
            target_obj[sk] = source_obj[sk]


def intersection(source_obj, target_obj):
    source_section_keys = analyse_ini(source_obj)
    target_section_keys = analyse_ini(target_obj)
    for sk in source_section_keys:
        if sk in target_section_keys:
            source_item_keys = analyse_section(source_obj[sk])
            target_item_keys = analyse_section(target_obj[sk])
            for ik in source_item_keys:
                if ik in target_item_keys:
                    target_obj[sk][ik] = source_obj[sk][ik]
                else:
                    pass
        else:
            pass


def check_file(file_path):
    return True if exists(file_path) else False


def init_arg_list(argument_paser):
    argument_paser.add_argument('-s',
                                '--source',
                                help='data source',
                                action='store')  # 配置数据源文件，即备份的用户配置
    argument_paser.add_argument('-t',
                                '--target',
                                help='data merge target',
                                action='store')  # 配置数据目标文件，即新版本用到的配置文件
    argument_paser.add_argument('-r',
                                '--rule',
                                help='follow the rules',
                                action='store_true')
    argument_paser.add_argument('-u',
                                '--union',
                                help='no matter data in A or in B, put all into B',
                                action='store_true')  # 并集式合入
    argument_paser.add_argument('-i',
                                '--intersection',
                                help='data both in A and in B, put it into B, drop the others',
                                action='store_true')  # 交集式合入


def check_args(argument_paser):
    if len(sys.argv) == 1:
        argument_paser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    ap = ArgumentParser()
    init_arg_list(ap)
    check_args(ap)
    args, remaining = ap.parse_known_args(sys.argv)
    main(args)
