# -*- coding: utf-8 -*-
from flask_cors import CORS
from flask import Flask, jsonify
import json
import os

app = Flask(__name__)
CORS(app)  
current_path = os.getcwd()
project_root = os.path.dirname(current_path)
json_path = os.path.join(project_root, "json", "dic.json")

def load_words():
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return ["111"]  # 若檔案不存在，回傳空列表

words_data = load_words()

@app.route('/api/words', methods=['GET'])

def get_words():
    return jsonify(words_data), 200, {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == '__main__':
    app.run(debug=True)
