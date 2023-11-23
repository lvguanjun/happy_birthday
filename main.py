#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/11/24 00:02:37
@Author  :   lvguanjun
@Desc    :   main.py
"""

from flask import Flask, jsonify, request
from flask.views import MethodView

from utils import BloomFilterManager, standardize_ip

app = Flask(__name__)


bloom_manager = BloomFilterManager()


class CountView(MethodView):
    def get(self):
        global bloom_manager
        return jsonify({"count": bloom_manager.count})

    def post(self):
        global bloom_manager
        bloom_filter = bloom_manager.bloom_filter
        user_ip = standardize_ip(request.headers.get("X-Real-IP"))

        if user_ip is None:
            return jsonify({"error": "Invalid IP address"}), 400

        if user_ip not in bloom_filter:
            bloom_filter.add(user_ip)
            bloom_manager.count += 1
            bloom_manager.save_data()
            message = "Thanks for your star!"
        else:
            message = "You have already starred!"

        return jsonify({"count": bloom_manager.count, "message": message})


app.add_url_rule("/birthday_api/count", view_func=CountView.as_view("count_view"))

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
