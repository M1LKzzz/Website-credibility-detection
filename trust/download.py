from __future__ import annotations
from tqdm import tqdm
import requests
import multitasking
import signal
from retry import retry
signal.signal(signal.SIGINT, multitasking.killall)

# 忽略安全警告
import urllib3
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
MB = 1024**2


def my_split(start: int, end: int, step: int) -> list[tuple[int, int]]:
    parts = [(start, min(start+step, end))
             for start in range(0, end, step)]
    return parts


def get_file_size(url: str, raise_error: bool = False) -> int:
    response = requests.head(url)
    file_size = response.headers.get('Content-Length')
    if file_size is None:
        if raise_error is True:
            raise ValueError('该文件不支持多线程分段下载！')
        return file_size
    return int(file_size)


# errror: http://terraplant.com.br/wp-content/y85olO3ItcfCphv/
def download(url: str, file_name: str, retry_times: int = 3, each_size=16*MB) -> None:
    f = open(file_name, 'wb')
    file_size = get_file_size(url)
    
    if file_size is not None:
        @retry(tries=retry_times)
        @multitasking.task
        def start_download(start: int, end: int) -> None:
            _headers = headers.copy()
            _headers['Range'] = f'bytes={start}-{end}'
            response = session.get(url, headers=_headers, stream=True)
            chunk_size = 128
            chunks = []
            for chunk in response.iter_content(chunk_size=chunk_size):
                chunks.append(chunk)
                bar.update(chunk_size)
            f.seek(start)
            for chunk in chunks:
                f.write(chunk)
            del chunks

        session = requests.Session()
        # print(f'{each_size}, {file_size}')
        each_size = min(each_size, file_size)

        parts = my_split(0, file_size, each_size)
        print(f'分块数：{len(parts)}')
        bar = tqdm(total=file_size, desc=f'下载文件：{file_name}')
        for part in parts:
            start, end = part
            start_download(start, end)
        multitasking.wait_for_tasks()
        f.close()
        bar.close()


if __name__ == '__main__':
    cnt = 0
    try:
        download('http://download.rising.com.cn/zsgj/ravmimail.exe', './sample/5bu')
    except:
        print(cnt)
        cnt += 1
        pass
    # download('http://41.89.94.30/web/attachments/5buyey63u3/', './sample/5bu')