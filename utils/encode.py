#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : encode.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Date  : 2022/8/29

import base64
import requests
import requests.utils
from time import sleep
import os
from utils.web import UC_UA,PC_UA
# import ddddocr

def getPreJs():
    base_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))  # 上级目
    lib_path = os.path.join(base_path, f'libs/pre.js')
    with open(lib_path,encoding='utf-8') as f:
        code = f.read()
    return code

def getCryptoJS():
    base_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))  # 上级目
    os.makedirs(os.path.join(base_path, f'libs'), exist_ok=True)
    lib_path = os.path.join(base_path, f'libs/crypto-hiker.js')
    # print('加密库地址:', lib_path)
    if not os.path.exists(lib_path):
        return 'undefiend'
    with open(lib_path,encoding='utf-8') as f:
        code = f.read()
    return code

def getHome(url):
    # http://www.baidu.com:9000/323
    urls = url.split('//')
    homeUrl = urls[0] + '//' + urls[1].split('/')[0]
    return homeUrl

def verifyCode(url,headers,timeout=5,total_cnt=3):
    lower_keys = list(map(lambda x: x.lower(), headers.keys()))
    host = getHome(url)
    if not 'referer' in lower_keys:
        headers['Referer'] = host
    print(f'开始自动过验证,请求头:{headers}')
    cnt = 0
    import ddddocr
    ocr = ddddocr.DdddOcr()
    while cnt < total_cnt:
        s = requests.session()
        try:
            img = s.get(url=f"{host}/index.php/verify/index.html", headers=headers,timeout=timeout).content
            code = ocr.classification(img)
            print(f'第{cnt+1}次验证码识别结果:{code}')
            res = s.post(
                url=f"{host}/index.php/ajax/verify_check?type=search&verify={code}",
                headers=headers).json()
            if res["msg"] == "ok":
                cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
                cookie_str = ';'.join([f'{k}={cookies_dict[k]}' for k in cookies_dict])
                # return cookies_dict
                return cookie_str
        except:
            print(f'第{cnt+1}次验证码提交失败')
            pass
        cnt += 1
        sleep(1)
    return ''

def base64Encode(text):
    return base64.b64encode(text.encode("utf8")).decode("utf-8") #base64编码

def baseDecode(text):
    return base64.b64decode(text).decode("utf-8") #base64解码

def dealObj(obj=None):
    if not obj:
        obj = {}
    encoding = obj.get('encoding') or 'utf-8'
    encoding = str(encoding).replace("'", "")
    # print(type(url),url)
    # headers = dict(obj.get('headers')) if obj.get('headers') else {}
    # headers = obj.get('headers').to_dict() if obj.get('headers') else {}
    headers = obj.get('headers') if obj.get('headers') else {}
    new_headers = {}
    # print(type(headers),headers)
    for i in headers:
        new_headers[str(i).replace("'", "")] = str(headers[i]).replace("'", "")
    # print(type(new_headers), new_headers)

    timeout = float(obj.get('timeout').to_int()) if obj.get('timeout') else None
    # print(type(timeout), timeout)
    body = obj.get('body') if obj.get('body') else {}
    new_body = {}
    for i in body:
        new_body[str(i).replace("'", "")] = str(body[i]).replace("'", "")
    return {
        'encoding':encoding,
        'headers':new_headers,
        'timeout':timeout,
        'body': new_body,
    }

def base_request(url,obj,method=None):
    url = str(url).replace("'", "")
    if not method:
        method = 'get'
    # print(obj)
    print(f'{method}:{url}')
    try:
        # r = requests.get(url, headers=headers, params=body, timeout=timeout)
        if method.lower() == 'get':
            r = requests.get(url, headers=obj['headers'], params=obj['body'], timeout=obj['timeout'])
        else:
            r = requests.post(url, headers=obj['headers'], data=obj['body'], timeout=obj['timeout'])
        # r = requests.get(url, timeout=timeout)
        # r = requests.get(url)
        # print(encoding)
        r.encoding = obj['encoding']
        # print(f'源码:{r.text}')
        return r.text
    except Exception as e:
        print(f'{method}请求发生错误:{e}')
        return ''

def fetch(url,obj,method=None):
    if not method:
        method = 'get'
    obj = dealObj(obj)
    # print(f'{method}:{url}')
    if not obj.get('headers') or not obj['headers'].get('User-Agent'):
        obj['headers']['User-Agent'] = PC_UA
    return base_request(url,obj,method)

def post(url,obj):
    obj = dealObj(obj)
    return base_request(url,obj,'post')

def request(url,obj,method=None):
    if not method:
        method = 'get'
    obj = dealObj(obj)
    # print(f'{method}:{url}')
    if not obj.get('headers') or not obj['headers'].get('User-Agent'):
        obj['headers']['User-Agent'] = UC_UA

    return base_request(url, obj, method)

def buildUrl(url,obj=None):
    url = str(url).replace("'", "")
    if not obj:
        obj = {}
    new_obj = {}
    for i in obj:
        new_obj[str(i).replace("'", "")] = str(obj[i]).replace("'", "")
    if not str(url).endswith('?'):
        url = str(url) + '?'
    prs = '&'.join([f'{i}={obj[i]}' for i in obj])
    url = (url + prs).replace('"','').replace("'",'')
    # print(url)
    return url