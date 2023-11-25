#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/11/24 00:02:31
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import ipaddress
import os
import shelve
import threading
import time
from datetime import datetime

import redis
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pybloom_live import BloomFilter

redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# Load environment variables from .env file
load_dotenv()


def standardize_ip(ip):
    try:
        return str(ipaddress.ip_address(ip))
    except ValueError:
        return None


class BloomFilterManager:
    def __init__(self, db_path="data.db", capacity=2000, error_rate=0.001):
        self.db_path = db_path
        self.capacity = capacity
        self.error_rate = error_rate
        self.bloom_filter, self.count = self.load_or_create_data()

    def load_or_create_data(self):
        with shelve.open(self.db_path) as db:
            bloom_filter = db.get("bloom_filter")
            count = db.get("count", 0)

            if bloom_filter is None:
                bloom_filter = BloomFilter(
                    capacity=self.capacity, error_rate=self.error_rate
                )
                db["bloom_filter"] = bloom_filter

            return bloom_filter, count

    def save_data(self):
        max_try_time = 3
        try_time = 0

        while try_time < max_try_time:
            try:
                with shelve.open(self.db_path, writeback=True) as db:
                    db["bloom_filter"] = self.bloom_filter
                    db["count"] = self.count
                break  # 如果成功，跳出循环
            except IOError:
                time.sleep(0.5)  # 保存失败，等待0.5秒后重试
                try_time += 1

        if try_time == max_try_time:
            raise IOError("save data failed")

    def start_persist_timer(self, interval=60):  # 默认间隔为1分钟
        self.persist_required = False
        self.persist_interval = interval
        threading.Thread(target=self._persist_timer).start()

    def _persist_timer(self):
        while True:
            time.sleep(self.persist_interval)
            if self.persist_required:
                self.save_data()
                self.persist_required = False

    def mark_persist_required(self):
        self.persist_required = True


def get_today_conversations_times():
    url = "https://dash.pandoranext.com/"
    headers = {
        "cookie": os.getenv("COOKIE"),
    }
    response = requests.get(url, headers=headers)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")
    usage_text = soup.find("span", class_="text-red-500 font-bold").text
    used_amount = usage_text.split("/")[0].strip()

    return int(used_amount)


def sum_all_pre_conversations_times():
    conversations_times = redis_client.hgetall("conversations_times")
    total = sum((int(i) for i in conversations_times.values()))
    return total


if __name__ == "__main__":
    data = get_today_conversations_times()
    today = datetime.now().strftime("%Y-%m-%d")
    redis_client.hset("conversations_times", today, data)
