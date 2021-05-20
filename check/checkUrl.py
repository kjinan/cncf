#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import time

file = open("../result/URL_Result.txt", "r")

for line in file:
    line = line.strip()
    print("== scanning ", line)
    try:
        response = requests.get(line, timeout=5)
    except:
        print('======= failed ', line)
        time.sleep(0.2)
file.close()
