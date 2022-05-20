from __future__ import annotations
import requests
import concurrent.futures
from retry import retry

# 忽略安全警告
import urllib3
urllib3.disable_warnings()

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
	}
MB = 1024**2


def get_file_size(url: str) -> int:
    file_size = requests.head(url).headers.get('Content-Length')
    if file_size is None:
        return 0  # 返回0，配合后续检查判断是否可下载文件
    return int(file_size)


# 分块
def my_split(len: int, step: int) -> list[tuple[int, int]]:
    parts = [(i, min(i+step, len)) for i in range(0, len, step)]
    return parts

# reference: https://blog.csdn.net/as604049322/article/details/119847193
def download(url: str, file_name: str, retry_times: int = 3, each_size=16*MB) -> None:
    file_size = get_file_size(url)
    print(f'size: {file_size}, url: {url}')
    
    if file_size <= 0:
        print(f'file download failed from {url}')
        return
    else:
        with open(file_name, 'wb') as f:

            @retry(tries=retry_times)
            def range_download(start: int, end: int) -> None:
                _headers = headers.copy()
                _headers['Range'] = f'bytes={start}-{end}'
                response = session.get(url, headers=_headers, stream=True)
                chunk_size = 16 * 1024
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)

            session = requests.Session()
            each_size = min(each_size, file_size)
            parts = my_split(file_size, each_size)
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for part in parts:
                    start, end = part
                    futures.append(executor.submit(range_download, start, end))
            concurrent.futures.as_completed(futures)


if __name__ == '__main__':
    try:
        requests.get('http://jladsj.jfasl.com')
    except requests.exceptions.ConnectionError as e:
        print('unknown')
    # download('https://cn.bing.com', './test_file')
    # download('http://41.89.94.30/web/attachments/5buyey63u3/', './sample/5bu')
    # http://download.rising.com.cn/zsgj/ravmimail.exe
    # https://www.voidtools.com/Everything-1.4.1.1015.x86.Lite-Setup.exe