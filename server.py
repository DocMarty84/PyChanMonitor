#!/usr/bin/env python
# coding: utf-8

import main
import config as c

import logging
from flask import Flask, render_template, request, jsonify
from flask_jsonrpc import JSONRPC

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__) # Flask application
jsonrpc = JSONRPC(app, '/add_url_json') # Flask-JSONRPC

# Test:
# curl -i -X POST -H "Content-Type: application/json; indent=4" \
#   -d '{
#     "id": "1",
#     "jsonrpc": "2.0",
#     "method": "App.add_url",
#     "params": {"url": "https://boards.4chan.org/wg/thread/6431912/i-like-these-kind-of-wallpapers"},
#   }' http://localhost:33333/add_url_json
@jsonrpc.method('App.add_url_json')
def add_url_json(url, password):
    if password != c.PASSWORD:
        return False
    data = url.split('/')
    board = data[3]
    thread = int(data[5])
    title = data[6] if len(data) >= 7 else ''

    main.add_thread(board, thread, com=title)
    return True

@app.route('/add_url', methods=['POST'])
def add_url():
    if request.form['password'] != c.PASSWORD:
        return jsonify(result=False)

    try:
        data = request.form['url'].split('/')
        board = data[3]
        thread = int(data[5])
        title = data[6] if len(data) >= 7 else ''

        main.add_thread(board, thread, com=title)
    except Exception as e:
        return jsonify(result=False)

    return jsonify(result=True)

@app.route('/json')
def index_json():
    return render_template('index.html', json=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=c.SERVER_INTERFACE, port=c.SERVER_PORT, debug=True)
