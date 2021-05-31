# coding:utf-8
import argparse
import os
import logging

import enchant

from util.cncf_util import have_no_letter, special_char_to_blank, camel_to_snake_case, is_code_file_code_line

d = enchant.Dict("en_US")
# print d.check("Hello")
# print d.check("Helo")

# 判断当前路径是否存在，没有则创建new文件夹
if not os.path.exists(r"../result/"):
    os.makedirs(r"../result/")

log_file = open('../result/Word_Detail.log', encoding="utf-8", mode="w")
logging.basicConfig(stream=log_file, format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

global WRONG_WORD, IGNORE_WORD, IGNORE_FILE_NAME, IGNORE_FILE_SUFFIX, IGNORE_PATH, FAIL_OPENED_FILES
# 检查结果
WRONG_WORD = dict()
# 忽略检查的目录
IGNORE_PATH = []
# 忽略检查的文件
IGNORE_FILE_NAME = [
    # git相关
    'CHANGELOG.md', 'SECURITY.md', 'CONTRIBUTING.md',
    'CONTRIBUTING_GUIDELINES.md', 'MAINTAINERS.md', 'RELEASE.md', '', '',
    # go相关
    'go.mod', 'go.sum',
    # 几个比较大的文件
    'compute-gen.go'
]
# 忽略检查的后缀
IGNORE_FILE_SUFFIX = [
    # 图片
    'png', 'svg', 'jpg', 'gif', 'ico', 'eps', 'bmp',
    # 字体
    'woff', 'woff2', 'ttf', 'eot',
    # 证书文件
    'pem', 'pub', 'key', 'crt',
    # js/html等特定的UI文件不扫描
    'js', 'html', 'toml', 'css', 'lib', 'snap',
    'webmanifest', 'scss', 'map', 'tsx', 'ts', 'less',
    # 好像是jeager项目的特殊文件
    'nocover', 'libsonnet', 'rst', 'tf', 'com_policy', 'ttar',
    'proto', 'com_user_data',
    # 其他类型
    'iso', 'json', 'yml', 'rollover', 'yaml', 'tmpl',
    'mk', 'xml', 'ini', 'conf', 'bazel', 'template',
    'rl', 'rb', 'cfg', 's', 'idx', 'ai', 'pdf',
    'psd', 'plist', 'pack', 'rc', 'bzl', 'lock',
    'code', 'out', 'mkd', 'ps1', 'fuzz', 'MIT',
    'j2', 'test', 'cer',
]

# 未能成功检查的文件
FAIL_OPENED_FILES = []

# 需要忽略检查的单词
IGNORE_WORD = []


def init_ignore_word():
    _ignore_word_file = open('../config/ignore_words.txt', "r", encoding='utf-8')
    _ignore_word_list = [item.strip().lower() for item in _ignore_word_file.readlines()]
    IGNORE_WORD.extend(_ignore_word_list)


def add_wrong(word):
    if word not in WRONG_WORD:
        WRONG_WORD[word] = 1
    else:
        WRONG_WORD[word] += 1


def print_wrong():
    # 按单词首字母排序
    logging.info("错误单词-按字母顺序排序：")
    sort_keys = sorted(WRONG_WORD.keys())
    for _word in sort_keys:
        logging.debug("%d\t%s" % (WRONG_WORD[_word], _word))

    # 按单词错误次数排序
    logging.info("错误单词-按错误次数排序：")
    sort_keys = sorted(WRONG_WORD.items(), key=lambda x: x[1])
    for _word in sort_keys:
        logging.debug("%d\t%s" % (_word[1], _word[0]))


def ignore_word(word):
    if word.lower() in IGNORE_WORD:
        return True
    else:
        return False


def check_line(filename, line_num, src_line):
    # go/python/sh等代码文件中，非注释内容，不检查
    if is_code_file_code_line(filename, src_line):
        return

    # 如果这一行是空行或没有英文字母，则直接跳过
    if have_no_letter(src_line):
        return

    # 如果这一行含有“==”，则大概率是注释的代码，可以直接跳过
    if '==' in src_line or '+=' in src_line or '-=' in src_line or '>=' in src_line or '<=' in src_line:
        return

    # 如果这一行中含有网址，则大概率存在非正常单词，可以直接跳过
    if 'http://' in src_line or 'https://' in src_line:
        return

    # 如果这一行含有github.com，则大概率存在非正常单词，这种可以直接跳过
    if 'github.com' in src_line:
        return

    # 替换文件内容中的特殊字符
    des_line = special_char_to_blank(src_line)

    # 将驼峰单词拆开
    des_line = camel_to_snake_case(des_line)

    for _word in des_line.split():
        check_word(filename, line_num, src_line, _word)


def check_word(filename, line_num, line, word):
    # 如果少于五个字母，则大概率是各种缩写什么的，直接忽略
    if len(word) < 5:
        return

    if ignore_word(word):
        return

    if word != "" and not d.check(word):
        logging.debug("在文件【%s】第【%d】行【%s】单词【%s】错误" % (filename, line_num, line, word))
        add_wrong(word)


def search(pwd):
    for _path, dir, files in os.walk(pwd.strip()):
        # 隐藏的目录不扫描
        if "\\." in _path:
            continue

        # 跳过忽略检查的目录
        ignore_path_flag = False
        for _ignore_path in IGNORE_PATH:
            if _ignore_path in _path:
                ignore_path_flag = True
                break

        if ignore_path_flag:
            continue

        for file in files:
            # 跳过不扫描的文件
            if file in IGNORE_FILE_NAME:
                continue

            # 隐藏的文件、没有后缀名的文件 都不扫描
            if file.startswith('.') or '.' not in file:
                continue

            # 文件名中含有特殊单词的也不扫描
            if 'LICENSE' in file:
                continue

            # 跳过不扫描的文件类型以及后缀名过长的文件
            file_suffix = file.split('.')[-1]
            if len(file_suffix) > 5 or file_suffix in IGNORE_FILE_SUFFIX:
                continue

            # 尝试打开文件
            filename = os.sep.join([_path, file])
            f = open(filename, "r", encoding='utf-8')
            try:
                src_content = f.readlines()
            except UnicodeDecodeError:
                FAIL_OPENED_FILES.append(filename)
                continue

            # 打印真正被扫描的文件名
            print("=====", filename)

            # 逐行查找
            line_num = 0
            for _line in src_content:
                line_num += 1
                _line = _line.strip()

                # 检查该行
                check_line(filename, line_num, _line)


if __name__ == '__main__':
    # path变量的值放入参数中获取
    parser = argparse.ArgumentParser(usage="检查代码错误", description="helpinfo.")
    parser.add_argument("path", help="待检查代码的路径")
    args = parser.parse_args()
    PATH = args.path

    init_ignore_word()
    search(PATH)
    print_wrong()
    for i in FAIL_OPENED_FILES:
        print('!!!!!!!!!!!!!!!!!!', i)
