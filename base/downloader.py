#!/usr/bin/env python
# coding: utf-8

from base.db import RssDB, Thread

import datetime
import json
import logging
from multiprocessing import Pool
import os
import re
import requests
import yaml

ROOT_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep + '..' + os.sep

l = logging.getLogger(__name__)

def download_mp(p, save_path, http_session):
    # Create necessary directory
    d = p.get('dir', '')
    if not os.path.exists(save_path + os.sep + d):
        try:
            os.makedirs(save_path + os.sep + d)
        except OSError:
            pass

    url = "https://i.4cdn.org/%s/%s%s" % (p['board'], p['tim'], p['ext'])
    r = http_session.get(url, stream=True, timeout=30)
    if r.status_code == 200:
        with open(save_path + os.sep + p.get('dir', '') + os.sep\
                + p['filename'] + '_' + p['tim'] + p['ext'], 'wb') as f:
            for chunk in r:
                f.write(chunk)


class DownloaderBase():
    def __init__(self):
        self.conf = self._load_config()

        # DB related stuff
        self.rssdb = RssDB(self.conf['db']['uri'], self.conf['down']['save_path'])
        self.db_engine = self.rssdb.db_engine
        self.db_session = self.rssdb.db_session

        # HTTP session
        self.http_session = self._login()

    def _login(self):
        http_session = requests.Session()
        return http_session

    ################################################################################################
    ################################################################################################
    #                                   Initialization methods                                     #
    ################################################################################################
    ################################################################################################

    def _load_config(self):
        f_path = ROOT_PATH + "config.yml"
        with open(f_path, "r") as f:
            conf = yaml.load(f)

            conf_final = conf.copy()
            conf_final['db']['uri'] = 'sqlite:///' + ROOT_PATH + conf_final['db']['name']

            return conf_final

    ################################################################################################
    ################################################################################################
    #                                    Main actions available                                    #
    ################################################################################################
    ################################################################################################

    def monitor(self):
        posts_to_down = 0
        pool = Pool(self.conf['down']['max_dl'])

        for thread in self.db_session.query(Thread).filter_by(active=True):
            try:
                data = self.http_session.get("https://a.4cdn.org/%s/thread/%s.json" %\
                    (thread.board, thread.no), timeout=30)
            except requests.exceptions.Timeout:
                continue

            if data.status_code == 404:
                thread.active = False
                continue

            if data.status_code != 200:
                l.warning("Got error code '%s'. Skipping thread...", data.status_code)
                continue

            data_json = {}
            try:
                data_json = json.loads(data.content.decode('UTF-8'))
            except ValueError:
                l.warning("Could not parse content of thread '%s' of board '%s'!",\
                    thread.no, thread.board)
                continue

            thread.date_updated = datetime.datetime.utcnow()
            for post in data_json.get('posts', []):
                # Get the title of the thread if not available
                if not thread.com:
                    thread.com = re.sub(r'\W+', '-',\
                        post.get('sub') or post.get('com') or str(post.get('no')))
                    thread.com = thread.com[:50]

                # Download post if necessary
                last_no = post.get('no', 9999999999999)
                if last_no > thread.last_no and post.get('filename'):
                    posts_to_down += 1
                    post_to_down = {
                        'dir': thread.com,
                        'board': thread.board,
                        'filename': str(post.get('filename', '')),
                        'tim': str(post.get('tim', '')),
                        'ext': str(post.get('ext', '')),
                    }
                    pool.apply_async(
                        download_mp,
                        args=(post_to_down, self.conf['down']['save_path'], self.http_session)
                    )
                    l.debug("Downloading %s", post_to_down['filename'])
            thread.last_no = last_no

        self.db_session.commit()
        pool.close()
        pool.join()

        if posts_to_down:
            l.info("%s file(s) downloaded!", posts_to_down)
        else:
            l.info("No file to download")


    def add_thread(self, board, no, com=''):
        if self.db_session.query(Thread).filter_by(board=board, no=no).first():
            return

        thread = Thread()
        thread.board = str(board)
        thread.no = int(no)
        thread.com = com
        thread.last_no = 0
        thread.active = True

        self.db_session.add(thread)
        self.db_session.commit()
        l.info("Thread '%s' of board '%s' added for monitoring", no, board)


    def clean(self):
        date_limit =\
            datetime.datetime.utcnow() - datetime.timedelta(days=self.conf['db']['max_age_days'])
        threads_removed = self.db_session.query(Thread)\
            .filter(Thread.date_updated < date_limit, Thread.active == False).delete()
        self.db_session.commit()
        l.info("%s threads(s) removed", threads_removed)


    def show(self):
        for thread in self.db_session.query(Thread).order_by(Thread.id):
            print(thread)
