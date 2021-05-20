# coding:gbk
import os
import logging

PATH = "D:\\workspace\\CNCF\\minikube"
logging.basicConfig(filename='../result/URL_Detail.log', format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

global IGNORE_FILE_SUFFIX, IGNORE_PATH, RESULT_URL, FAIL_OPENED_FILES
# ���Լ��ĺ�׺
IGNORE_FILE_SUFFIX = [
    # ͼƬ
    'png', 'svg', 'jpg', 'gif', 'ico', 'eps', 'bmp',
    # ����
    'woff', 'woff2', 'ttf', 'eot',
    # js�ļ���ɨ��
    'js',
    # ��������
    'iso',
]
# ���Լ���Ŀ¼
IGNORE_PATH = ['.circleci', '.git', '.github']
# �����
RESULT_URL = []

# δ�ܳɹ������ļ�
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

    # �������󱾵ص�url
    if '://localhost' in url_str or '://127.0.0.1' in url_str:
        return

    # �����github���Ӳ���¼:issues
    if '://github.com' in url_str and '/issues/' in url_str:
        return

    # �����github���Ӳ���¼:issues
    if '://github.com' in url_str and '/pull/' in url_str:
        return

    # ��¼url�����ļ�λ��
    logging.debug("�ڡ�%s���ļ��ڡ�%d���С�%s���������ӡ�%s��" % (filename, line_num, line, url_str))

    # ����url������Ϣ�����ظ���¼
    if url_str not in RESULT_URL:
        RESULT_URL.append(url_str)
        return


def check_line_url(filename, line_num, line):
    if "http:" not in line and 'https:' not in line:
        return

    # ������http��ַ��https��ַ
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
        # �������Լ���Ŀ¼
        ignore_path_flag = False
        for _ignore_path in IGNORE_PATH:
            if _ignore_path in _path:
                ignore_path_flag = True
                break
        if ignore_path_flag:
            continue

        for file in _files:
            # ������ɨ����ļ�����
            file_suffix = file.split('.')[-1]
            if file_suffix in IGNORE_FILE_SUFFIX:
                continue

            # if file_suffix != 'md' and file_suffix != 'MD':
            #     continue

            # ���Դ��ļ�
            filename = os.sep.join([_path, file])
            f = open(filename, "r", encoding='utf-8')
            try:
                content = f.readlines()
            except UnicodeDecodeError:
                FAIL_OPENED_FILES.append(filename)
                continue

            # ��ӡ������ɨ����ļ���
            print("=====", filename)

            line_num = 0
            for _line in content:
                line_num += 1
                _line = _line.strip()
                # ����Ƿ���url
                check_line_url(filename, line_num, _line)


search(PATH)
save_url_result()
for i in FAIL_OPENED_FILES:
    print('!!!!!!!!!!!!!!!!!!', i)
