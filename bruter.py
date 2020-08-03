# coding=utf-8

import urllib3
urllib3.disable_warnings()

import threading
import queue
import requests
from tqdm import tqdm
import time
import sys

from lib.logger import logger
from lib.header_generator import get_headers

class WebDirBruter:
    def __init__(self, params):
        self.url = params.url.rstrip('/')
        self.filename = params.filename
        self.count = params.count
        self.sleep_time = params.sleep

    class BruteScan(threading.Thread):
        def __init__(self, work_queue, progress_bar):
            threading.Thread.__init__(self)
            self.work_queue = work_queue
            self.progress_bar = progress_bar
            self.lock = threading.Lock()

        def run(self):
            while not self.work_queue.empty():
                self.progress_bar.update(1)
                url = self.work_queue.get()
                try:
                    response = requests.get(url=url, headers=get_headers(), timeout=10, verify=False)
                    # 响应状态码不为4xx和5xx即判定为存在Web目录
                    if response.status_code < 400:
                        logger.info("!!!Found Web Dir: " + url)
                        filename = url.split("://")[1].split("/")[0].replace(".", "_")
                        # 写文件需要加锁
                        self.lock.acquire()
                        with open("./result/" + filename + ".txt", "a+") as f:
                            f.write(url + "\n")
                        self.lock.release()
                except Exception as e:
                    print(e)
            self.progress_bar.close()

    def start(self):
        print("[*]Start to scan url:", self.url)
        logger.info("Start scanning...")
        work_queue = queue.Queue()

        with open(self.filename, 'r') as f:
            for i in f:
                work_queue.put(self.url + i.rstrip('\n').rstrip('\r'))

        progress_bar = tqdm(total=work_queue.qsize(), leave=False)
        progress_bar.set_description("Scan progress")

        threads = []
        thread_count = int(self.count)

        for i in range(thread_count):
            threads.append(self.BruteScan(work_queue, progress_bar))
        for i in threads:
            i.setDaemon(True)
            i.start()

        while True:
            if threading.activeCount() <= 1:
                break
            else:
                try:
                    time.sleep(self.sleep_time)
                except KeyboardInterrupt:
                    print("[*]User abort.")
                    logger.error("User abort!")
                    sys.exit(1)

        logger.info("Scan finished!")
        logger.info("Scan result is saved in ./result/ directory.")
        print("[*]Finished.")
        print("[*]Scan result is saved in ./result/ directory.")
