# -*- coding: utf-8 -*-
from flask_cors import CORS
from flask import Flask, request, jsonify
import json
import os
from db import  get_due_groups, review_word_group,check_review,create_word_group

app = Flask(__name__)
CORS(app)
# @app.route("/add_group", methods=["POST"])
# def add_group():
    # data = request.json
    # words = data.get("words", [])
# 
    # if not words or len(words) != 10:
        # return jsonify({"error": "10 個單字一組"}), 400
# 
    # add_word_group(words)
    # return jsonify({"message": "單字組已新增"})

@app.route("/due_groups", methods=["GET"])
#開始自動載入
def due_groups():
    print("嘗試get單字")
    groups = get_due_groups()
    print("groups內容:", groups)
    return jsonify(groups)

@app.route("/review/<int:group_id>", methods=["POST"])
#手動按鈕 完畢按鈕
def review(group_id):
    result = review_word_group(group_id)
    return jsonify({"message": result})

@app.route("/check_review", methods=["POST"])
#自動更新
def check():
    check_review()
    return jsonify({"message": "Success"})
#手動創建 單字群
@app.route("/create_word_group", methods=["POST"])
def create_group():
    result = create_word_group()
    return jsonify({"message": result})


if __name__ == "__main__":
    app.run(debug=True)



