# coding:utf-8
import os
import logging

import enchant

from util.cncf_util import have_no_letter, special_char_to_blank, camel_to_snake_case

d = enchant.Dict("en_US")
# print d.check("Hello")
# print d.check("Helo")

PATH = "D:\\workspace\\CNCF\\prometheus\\tsdb"
# PATH = "D:\\workspace\\CNCF\\test"

log_file = open('../result/Word_Detail.log', encoding="utf-8", mode="w")
logging.basicConfig(stream=log_file, format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

global WRONG_WORD, IGNORE_WORD, IGNORE_FILE_SUFFIX, IGNORE_PATH, FAIL_OPENED_FILES
# 检查结果
WRONG_WORD = dict()

# 忽略检查的后缀
IGNORE_FILE_SUFFIX = [
    # 图片
    'png', 'svg', 'jpg', 'gif', 'ico', 'eps', 'bmp',
    # 字体
    'woff', 'woff2', 'ttf', 'eot',
    # js文件不扫描
    'js',
    # 其他类型
    'iso', 'json',
]
# 忽略检查的目录
IGNORE_PATH = ['.circleci', '.git', '.github']

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
    logging.info("错误单词：\n")
    for _word in WRONG_WORD:
        logging.debug("===>【%s】【%d】" % (_word, WRONG_WORD[_word]))


def ignore_word(word):
    if word.lower() in IGNORE_WORD:
        return True
    else:
        return False


def check_line(filename, line_num, src_line):
    # go文件，不是以“//”开头的注释内容，不检查
    if filename.endswith('.go') and (not src_line.startswith('//') or src_line.startswith('// TODO')):
        return

    # 如果这一行是空行或没有英文字母，则直接跳过
    if have_no_letter(src_line):
        return

    # 如果这一行含有“==”，则大概率是注释的代码，可以直接跳过
    if '==' in src_line or '+=' in src_line or '-=' in src_line:
        return

    # 如果这一行中含有网址，则大概率存在非正常单词，可以直接跳过
    if 'http://' in src_line or 'https://' in src_line:
        return

    # 替换文件内容中的特殊字符
    des_line = special_char_to_blank(src_line)

    # 将驼峰单词拆开
    des_line = camel_to_snake_case(des_line)

    for _word in des_line.split():
        check_word(filename, line_num, src_line, _word)


def check_word(filename, line_num, line, word):
    if ignore_word(word):
        return

    if word != "" and not d.check(word):
        logging.debug("在文件【%s】第【%d】行【%s】单词【%s】错误" % (filename, line_num, line, word))
        add_wrong(word)


def search(pwd):
    for _path, dir, files in os.walk(pwd.strip()):
        # 跳过忽略检查的目录
        ignore_path_flag = False
        for _ignore_path in IGNORE_PATH:
            if _ignore_path in _path:
                ignore_path_flag = True
                break
        if ignore_path_flag:
            continue

        for file in files:
            # 跳过不扫描的文件类型
            file_suffix = file.split('.')[-1]
            if not file_suffix:
                print('~~~~~~~~~~~~~~~~~~~~~~~', file)
                continue
            if file_suffix in IGNORE_FILE_SUFFIX:
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
    init_ignore_word()
    search(PATH)
    print_wrong()
    for i in FAIL_OPENED_FILES:
        print('!!!!!!!!!!!!!!!!!!', i)