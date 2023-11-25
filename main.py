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

from utils import BloomFilterManager, get_conversations_times, standardize_ip

app = Flask(__name__)


post_bloom_manager = BloomFilterManager()
post_bloom_manager.start_persist_timer()

get_bloom_manager = BloomFilterManager(db_path="get_data.db", capacity=5000)
get_bloom_manager.start_persist_timer()


class CountView(MethodView):
    def handle_request(self, method):
        user_ip = standardize_ip(request.headers.get("CF-Connecting-IP"))
        if user_ip is None:
            return jsonify({"message": "Invalid IP address"}), 400

        manager = post_bloom_manager if method == "post" else get_bloom_manager
        bloom_filter = manager.bloom_filter

        if manager.count >= manager.capacity:
            message = "Thanks for everyone's star!" if method == "post" else None
            return jsonify({"count": manager.count, "message": message})

        if user_ip not in bloom_filter:
            bloom_filter.add(user_ip)
            manager.count += 1
            manager.mark_persist_required()
            message = "Thanks for your star!" if method == "post" else None
        else:
            message = "You have already starred!" if method == "post" else None

        return jsonify({"count": manager.count, "message": message})

    def get(self):
        return self.handle_request("get")

    def post(self):
        return self.handle_request("post")


class ShowView(MethodView):
    def get(self):
        get_count_times = get_bloom_manager.count
        star_times = post_bloom_manager.count
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
