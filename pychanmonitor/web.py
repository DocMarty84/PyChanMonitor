#!/usr/bin/env python
# coding: utf-8

import logging
import logging.handlers
import os

from flask import Flask, render_template, request, jsonify

from downloader import DownloaderBase

LOG_FILENAME = '..' + os.sep + 'pychanmonitor.log'

l = logging.getLogger(__name__)
app = Flask(__name__) # Flask application


####################################################################################################
####################################################################################################
#                                          Flask JSONRPC                                           #
####################################################################################################
####################################################################################################

# # Test:
# # curl -i -X POST -H "Content-Type: application/json; indent=4" \
# #   -d '{
# #     "id": "1",
# #     "jsonrpc": "2.0",
# #     "method": "App.add_url",
# #     "params": {"url": "https://boards.4chan.org/wg/thread/6431912/i-like-these-kind-of-wallpapers"},
# #   }' http://localhost:33333/add_url_json

# from flask_jsonrpc import JSONRPC
# jsonrpc = JSONRPC(app, '/add_url_json') # Flask-JSONRPC
# @jsonrpc.method('App.add_url_json')
# def add_url_json(url, password):
#     down_route = DownloaderBase()
#     if password != down_route.conf['server']['password']:
#         return False
#     data = url.split('/')
#     board = data[3]
#     thread = int(data[5])
#     title = data[6] if len(data) >= 7 else ''
#
#     down_route.add_thread(board, thread, com=title)
#     return True
#
# @app.route('/json')
# def index_json():
#     return render_template('index.html', json=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        down_route = DownloaderBase()
        if request.form['password'] != down_route.conf['server']['password']:
            return jsonify(result=False)

        try:
            data = request.form['url'].split('/')
            board = data[3]
            thread = int(data[5])
            title = data[6] if len(data) >= 7 else ''

            down_route.add_thread(board, thread, com=title)
        except Exception as e:
            return jsonify(result=False)

        return jsonify(result=True)
    return render_template('index.html')

if __name__ == '__main__':
    # Logging stuff
    loglevel = logging.WARNING
    f = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=5)
    fh.setLevel(loglevel)
    fh.setFormatter(f)
    sh = logging.StreamHandler()
    sh.setLevel(loglevel)
    sh.setFormatter(f)
    logging.basicConfig(level=loglevel, handlers=[fh, sh])

    # Load configration
    down = DownloaderBase()
    app.run(host=down.conf['server']['interface'], port=down.conf['server']['port'], debug=True)
