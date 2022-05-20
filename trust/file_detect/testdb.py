import sqlite3
import time
import yara
import os
from download import *

conn = sqlite3.connect('sample.db')
cursor = conn.cursor()

conn.execute("drop table sample")
conn.execute("CREATE TABLE SAMPLE(id integer primary key autoincrement, name text, url text, sha256 text, cve_rules text, exploit_kits text, maldocs text, malware text, mobile_malware text)")
# conn.execute("INSERT INTO SAMPLE(url) VALUES(?)", ('ddd',))

conn.commit()
conn.close()


# url = 'http://terraplant.com.br/wp-content/y85olO3ItcfCphv/'
# filesize = get_file_size(url)
# if filesize is not None and filesize > 20*MB:
#     print("Safe size")
# else:
#     if url[-1] == '/':
#         filename = url.split('/')[-2]  # such as: http://xxx.xxx.xxx/abc.exe/
#     else:
#         filename = url.split('/')[-1]  # such as: http://xxx.xxx.xxx/abc.exe
#     for i in range(10):
#         try:
#             download(url, "./sample/" + filename)
#         except Exception as e:
#             if i > 9:
#                 with open('download.log', 'a') as f:
#                     f.write(e)
#             else:
#                 time.sleep(0.5)
#                 print(i)
#         else:
#             time.sleep(0.1)
#             break



