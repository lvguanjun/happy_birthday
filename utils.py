#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/11/24 00:02:31
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import shelve
import time

from pybloom_live import BloomFilter
import ipaddress


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
