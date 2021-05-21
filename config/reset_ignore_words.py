f = open('ignore_words.txt', "r+", encoding='utf-8')

# 读取内容
contents = f.readlines()

# 清空文件
f.seek(0)
f.truncate()
f.flush()

# 将内容排重、排序后重新写入
new_contents = [item.replace(' ', '') for item in set(contents)]
new_contents.sort()
f.writelines(new_contents)
f.flush()

print(1)
