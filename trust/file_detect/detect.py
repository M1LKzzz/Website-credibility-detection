import sqlite3
import os
import requests
import hashlib
import re
import yara
import time
from trust.file_detect.download import get_file_size, download

rule_types = ['cve_rules', 'exploit_kits', 'malware', 'mobile_malware'] # email

# Get the page source
def extract_html(url: str):
	header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
	}
	try:
		raw = requests.get(url, headers = header, timeout=3, verify=False)
		raw = raw.content.decode("utf-8", "ignore")
		return raw
	except:
		return None

# '(https?|ftp|file)?:?//[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
def extract_download_urls(url: str) -> list[str]:
    html = extract_html(url)
    prefix_url = r'https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
    suffixes_url = [r'\.exe', r'\.zip', r'\.tar.gz', r'\.deb', r'\.rpm', r'\.dmg', r'\.iso', r'\.tar.bz2', r'\.msi', r'\.pkg']
    result = []
    for suffix in suffixes_url:
        pattern = re.compile(prefix_url + suffix)
        if html:
            find_list = pattern.findall(html)
            if find_list:
                for i in find_list:
                    result.append(i)
                    # print(i)
    return result

# download file and return filename|None
def download_file(url) -> str:
    filesize = get_file_size(url)
    if filesize > 50 * (1024**2):  # 不下载大于100M的文件
        print(f"file too large which from {url}.")
        return
    else:
        if url[-1] == '/':  # such as: http://xxx.xxx.xxx/abc.exe/
            filename = url.split('/')[-2]
        else:               # such as: http://xxx.xxx.xxx/abc.exe
            filename = url.split('/')[-1]
        download(url, "trust/file_detect/sample/" + filename)
        print(filename)
        return filename


# 返回dict{rule_type: {matches}}
def yara_match(filepath: str):
    matches = {}
    doc_suffix = [r'txt', r'doc', r'docx', r'\.md', r'pdf']
    for rule_type in rule_types:
        rule_filename = 'trust/file_detect/yara-rules/' + rule_type + '_index.yar'
        rules = yara.compile(rule_filename)
        match = rules.match(filepath)
        if match:
            # conn.execute("UPDATE SAMPLE SET %s=? WHERE name=?" % rule_type, (str(matches)[1:-1], filename))  # str(matches): [suspicious_packer_section, UPX]
            # conn.commit()
            matches[rule_type] = match
    if filepath.split('.')[-1] in doc_suffix:
        rules = yara.compile('yara-rules/maldocs_index.yar')
        match = rules.match(filepath)
        if match:
            matches['maldocs'] = match
    return matches

# 功能模块，url->文件检测结果输出
def file_detect(origin_url) -> bool:
    urls = extract_download_urls(origin_url)
    cnt = 0  # 文件计数器
    result = {}
    for url in urls:
        try:
            filename = download_file(url)
        except:
            filename = None
        if filename:
            filepath = 'trust/file_detect/sample/' + filename
            with open(filepath, 'rb') as f:
                hexdigest = hashlib.sha256(f.read()).hexdigest()

            matches = {}
            conn = sqlite3.connect('trust/file_detect/sample.db')
            cursor = conn.cursor()
            # 只获取yara匹配结果的列
            query = cursor.execute(f"SELECT {', '.join(rule_types)} FROM SAMPLE WHERE sha256=?", (hexdigest,)).fetchall()
            if query:
                print(f"file result already exist, sha256: {hexdigest}")
                # print(query[0])  # 列表中只含一个元组结果
                for i in range(len(rule_types)):
                    # 索引具有对应关系
                    # 构造列表，使matches的value都为list, type(matches): list[str]
                    if query[0][i]:  # 非None时加入
                        matches[rule_types[i]] = [query[0][i]]  
                        # print((query[0][i]))
            else:  # 数据库中无记录
                conn.execute("INSERT INTO SAMPLE(name, url, sha256) VALUES(?, ?, ?)", (filename, url, hexdigest))
                matches = yara_match(filepath)
                for rule_type, match in matches.items():  # 此match为yara库的对象, type(match): list[yara.Match]
                    conn.execute(f"UPDATE SAMPLE SET {rule_type}=?", (str(match),))  # 存入字符串
                conn.commit()
            conn.close()
            result[cnt] = matches
            cnt += 1

    print(f'yara_matches: {result}')
    flag = False
    for idx, matches in result.items():
        for rule, match in matches.items():
            print(f"rule:{rule}, match:{match}")
            if match:  # 列表非空
                flag = True
    print(f'file_detect:{flag}')
    return flag


if __name__ == "__main__":
    # t1 = time.time()
    url = "https://www.onlinedown.net/soft/613750.htm"
    if (file_detect(url)):
        print("文件可疑")
    # print((time.time()-t1))
