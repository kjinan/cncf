# coding:gbk
import os
import logging

PATH = "D:\\workspace\\CNCF\\minikube"
logging.basicConfig(filename='../result/URL_Detail.log', format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

global IGNORE_FILE_SUFFIX, IGNORE_PATH, RESULT_URL, FAIL_OPENED_FILES
# 忽略检查的后缀
IGNORE_FILE_SUFFIX = [
    # 图片
    'png', 'svg', 'jpg', 'gif', 'ico', 'eps', 'bmp',
    # 字体
    'woff', 'woff2', 'ttf', 'eot',
    # js文件不扫描
    'js',
    # 其他类型
    'iso',
]
# 忽略检查的目录
IGNORE_PATH = ['.circleci', '.git', '.github']
# 检查结果
RESULT_URL = []

# 未能成功检查的文件
FAIL_OPENED_FILES = []


def save_url_result():
    f = open("../result/URL_Result.txt", "w", encoding='utf-8')
    RESULT_URL.sort()
    for line in RESULT_URL:
        f.write(line + "\n")
    f.close()


def check_str_url(filename, line_num, line, url_str):
    if not url_str:
        return

    # 忽略请求本地的url
    if '://localhost' in url_str or '://127.0.0.1' in url_str:
        return

    # 特殊的github链接不记录:issues
    if '://github.com' in url_str and '/issues/' in url_str:
        return

    # 特殊的github链接不记录:issues
    if '://github.com' in url_str and '/pull/' in url_str:
        return

    # 记录url所在文件位置
    logging.debug("在【%s】文件第【%d】行【%s】存在链接【%s】" % (filename, line_num, line, url_str))

    # 保存url汇总信息，不重复记录
    if url_str not in RESULT_URL:
        RESULT_URL.append(url_str)
        return


def check_line_url(filename, line_num, line):
    if "http:" not in line and 'https:' not in line:
        return

    # 解析出http地址和https地址
    for _url_str in line.split():
        if "http:" in _url_str and "http://" == _url_str[:7] and len(_url_str) > 8:
            http_url = _url_str.replace('"', '').replace('>', '').replace('}', '') \
                .replace(',', '').replace('(', '').replace(')', ''). \
                replace("'", '').strip(":").strip(".").strip("]").strip("{").strip("\\n")
            check_str_url(filename, line_num, line, http_url)

        if "https:" in _url_str and "https://" == _url_str[:8] and len(_url_str) > 9:
            https_url = _url_str.replace('"', '').replace('>', '').replace('}', '') \
                .replace(',', '').replace('(', '').replace(')', ''). \
                replace("'", '').strip(":").strip(".").strip("]").strip("{").strip("\\n")
            check_str_url(filename, line_num, line, https_url)


def search(pwd):
    for _path, _dir, _files in os.walk(pwd.strip()):
        # 跳过忽略检查的目录
        ignore_path_flag = False
        for _ignore_path in IGNORE_PATH:
            if _ignore_path in _path:
                ignore_path_flag = True
                break
        if ignore_path_flag:
            continue

        for file in _files:
            # 跳过不扫描的文件类型
            file_suffix = file.split('.')[-1]
            if file_suffix in IGNORE_FILE_SUFFIX:
                continue

            # if file_suffix != 'md' and file_suffix != 'MD':
            #     continue

            # 尝试打开文件
            filename = os.sep.join([_path, file])
            f = open(filename, "r", encoding='utf-8')
            try:
                content = f.readlines()
            except UnicodeDecodeError:
                FAIL_OPENED_FILES.append(filename)
                continue

            # 打印真正被扫描的文件名
            print("=====", filename)

            line_num = 0
            for _line in content:
                line_num += 1
                _line = _line.strip()
                # 检查是否含有url
                check_line_url(filename, line_num, _line)


search(PATH)
save_url_result()
for i in FAIL_OPENED_FILES:
    print('!!!!!!!!!!!!!!!!!!', i)
