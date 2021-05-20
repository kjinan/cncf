import re


# 判断是否是具体的代码
def is_code_file_code_line(filename, line):
    _line = line.strip()
    # go文件
    if (filename.endswith('.go') or filename.endswith('.proto')) and not _line.startswith('//'):
        return True
    # py文件
    if filename.endswith('.py') and not _line.startswith('#'):
        return True
    # sh文件
    if filename.endswith('.sh') and not _line.startswith('#'):
        return True

    return False


# 特殊字符替换成空格
def special_char_to_blank(text):
    result = re.sub('[^a-zA-Z\n\.]', ' ', text)
    result = result.replace('.', ' ')
    return result


# 校验字符串中是否含有英文字母
def have_no_letter(text):
    if not len(text):
        return True

    letter_re = re.compile(r'[A-Za-z]', re.S)
    letter_num = re.findall(letter_re, text)
    if len(letter_num):
        return False
    else:
        return True


# 驼峰拆开并用空格分隔
def camel_to_snake_case(text):
    matches = re.finditer('[A-Z]', text)

    contents = []
    last_start = 0
    for it in matches:
        start, end = it.span()
        if start > 0:
            contents.append(text[last_start:start])

        last_start = start

    contents.append(text[last_start:])

    return ' '.join(contents).lower()


if __name__ == '__main__':
    camel_text = 'ILoveYouVeryMuch'
    snake_text = camel_to_snake_case(camel_text)

    print("{} => {}".format(camel_text, snake_text))
    print(camel_text.lower().replace('_', '') == snake_text.replace('_', ''))
