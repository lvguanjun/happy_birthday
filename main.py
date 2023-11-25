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

from utils import BloomFilterManager, standardize_ip, get_conversations_times

app = Flask(__name__)


bloom_manager = BloomFilterManager()
get_count_times = 0


class CountView(MethodView):
    def get(self):
        global get_count_times
        global bloom_manager
        get_count_times += 1
        return jsonify({"count": bloom_manager.count})

    def post(self):
        global bloom_manager
        bloom_filter = bloom_manager.bloom_filter
        user_ip = standardize_ip(request.headers.get("CF-Connecting-IP"))

        if user_ip is None:
            return jsonify({"message": "Invalid IP address"}), 400

        if bloom_manager.count >= bloom_manager.capacity:
            return jsonify(
                {"count": bloom_manager.count, "message": "Thanks for everyone's star!"}
            )

        if user_ip not in bloom_filter:
            bloom_filter.add(user_ip)
            bloom_manager.count += 1
            bloom_manager.save_data()
            message = "Thanks for your star!"
        else:
            message = "You have already starred!"

        return jsonify({"count": bloom_manager.count, "message": message})


class ShowView(MethodView):
    def get(self):
        global get_count_times
        star_times = bloom_manager.count
        conversations_times = get_conversations_times()
        return jsonify(
            {
                "star_times": star_times,
                "conversations_times": conversations_times,
                "get_count_times": get_count_times,
            }
        )


@app.errorhandler(Exception)
def handle_error(e):
    print(e)
    return jsonify({"message": "Sorry, something went wrong!"}), 500


app.add_url_rule("/birthday_api/count", view_func=CountView.as_view("count_view"))
app.add_url_rule("/birthday_api/show", view_func=ShowView.as_view("show_view"))

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
