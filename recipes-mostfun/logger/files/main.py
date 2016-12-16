#!/usr/bin/env python
# coding: utf-8
import sys
from argparse import ArgumentParser
import logging
from time import localtime
from time import strftime


def main(*args):
    param = args[0]

    print(param)
    now = localtime()
    today = strftime('%Y%m%d', now)
    filename = '/home/logs/{name}.log'.format(name=today)

    msg = ' {filename} | {function} | {lineno} | {message} '.format(filename=param.file, function=param.caller, lineno=param.line, message=param.msg)

    with open(filename, 'a') as f:
        logger = logging.getLogger(today)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename)
        fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s \n'))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        if param.debug:
            logger.debug(msg)
        elif param.info:
            logger.info(msg)
        elif param.warn:
            logger.warning(msg)
        elif param.error:
            logger.error(msg)
        else:
            logger.critical(msg)


def init_arg_list(argument_paser):
    argument_paser.add_argument('-f',
                                '--file',
                                help='action file',
                                action='store')
    argument_paser.add_argument('-c',
                                '--caller',
                                help='caller function',
                                action='store')
    argument_paser.add_argument('-l',
                                '--line',
                                help='action line',
                                action='store')
    argument_paser.add_argument('-d',
                                '--debug',
                                help='debug data',
                                action='store_true')
    argument_paser.add_argument('-i',
                                '--info',
                                help='info data',
                                action='store_true')
    argument_paser.add_argument('-w',
                                '--warn',
                                help='warn data',
                                action='store_true')
    argument_paser.add_argument('-e',
                                '--error',
                                help='erro data',
                                action='store_true')
    argument_paser.add_argument('-m',
                                '--msg',
                                help='message',
                                action='store')


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
