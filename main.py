#!/usr/bin/env python
# coding: utf-8
import config as c

import datetime
import getopt
import json
import logging as l
from multiprocessing import Pool
import os
import re
import requests
import sys

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
l.basicConfig(level=l.DEBUG)

class Thread(Base):
    __tablename__ = 'thread'

    id = Column(Integer, primary_key=True)
    board = Column(String)
    no = Column(Integer)
    com = Column(String)
    last_no = Column(Integer)
    date_updated = Column(DateTime)
    active = Column(Boolean)

    def __repr__(self):
        return """
        <Thread '%s'
            board='%s'
            no='%s'
            com='%s'
            last_post='%s',
            active='%s')
        >"""\
        % (self.id, self.board, self.no, self.com, self.last_no, self.active)


def init():
    engine = create_engine(c.DB)
    Session = sessionmaker(bind=engine)
    return {'engine': engine, 'session': Session()}


def install():
    db = init()
    Base.metadata.create_all(db['engine'])
    db['session'].commit()
    l.info('Database created')


def check_config():
    if not os.path.exists(c.SAVE_PATH):
        try:
            os.mkdir(c.SAVE_PATH)
        except OSError:
            pass

    db_session = init()['session']
    try:
        db_session.execute('SELECT * FROM thread')
    except OperationalError:
        install()


def download_single(p):
    url = "https://i.4cdn.org/%s/%s%s" % (p['board'], p['tim'], p['ext'])
    r = requests.get(url, stream=True, timeout=30)
    if r.status_code == 200:
        with open(c.SAVE_PATH + os.sep + p.get('dir', '') + os.sep\
                + p['filename'] + '_' + p['tim'] + p['ext'], 'wb') as f:
            for chunk in r:
                f.write(chunk)


def download_multi(posts_to_down):
    # Create necessary directories
    for d in {p.get('dir', '') for p in posts_to_down}:
        if not os.path.exists(c.SAVE_PATH + os.sep + d):
            try:
                os.makedirs(c.SAVE_PATH + os.sep + d)
            except OSError:
                pass

    pool = Pool(c.MAX_DL)
    for p in posts_to_down:
        pool.apply_async(download_single, (p,))
    pool.close()
    pool.join()


def monitor():
    db_session = init()['session']
    threads = db_session.query(Thread).filter_by(active=True)
    http_session = requests.Session()

    posts_to_down = []
    for thread in threads:
        try:
            data = http_session.get("https://a.4cdn.org/%s/thread/%s.json" %\
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
            l.warning("Could not parse content of thread '%s' of board '%s' added for monitoring",\
                thread.no, thread.board)
            continue

        thread.date_updated = datetime.datetime.utcnow()
        for post in data_json.get('posts', []):
            if not thread.com:
                thread.com = re.sub(r'\W+', '-',\
                    post.get('sub') or post.get('com') or str(post.get('no')))
                thread.com = thread.com[:50]
            last_no = post.get('no', 9999999999999)
            if last_no > thread.last_no and post.get('filename'):
                posts_to_down.append({
                    'dir': thread.com,
                    'board': thread.board,
                    'filename': str(post.get('filename', '')),
                    'tim': str(post.get('tim', '')),
                    'ext': str(post.get('ext', '')),
                })
        thread.last_no = last_no

    db_session.commit()

    if posts_to_down:
        l.info("%s file(s) to download...", len(posts_to_down))
        download_multi(posts_to_down)
        l.info("Download finished!")
    else:
        l.info("No file to download")


def add_thread(board, no, com=''):
    db = init()
    if db['session'].query(Thread).filter_by(board=board, no=no).first():
        return

    thread = Thread()
    thread.board = str(board)
    thread.no = int(no)
    thread.com = com
    thread.last_no = 0
    thread.active = True

    db['session'].add(thread)
    db['session'].commit()
    l.info("Thread '%s' of board '%s' added for monitoring", no, board)


def clean():
    db_session = init()['session']
    date_limit = datetime.datetime.utcnow() - datetime.timedelta(days=c.MAX_AGE_DAYS)
    threads_removed = db_session.query(Thread)\
        .filter(Thread.date_updated < date_limit, Thread.active == False).delete()
    db_session.commit()
    l.info("%s threads(s) removed", threads_removed)


def show():
    session = init()['session']
    for thread in session.query(Thread).order_by(Thread.id):
        print(thread)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "amvf:d", ["all", "monitor", "clean", "follow", "debug"])

    except getopt.GetoptError:
        l.critical("Incorrect parameters. Exiting...")
        sys.exit(2)

    check_config()

    # Parse arguments
    do_monitor = do_debug = do_clean = False
    board = thread = ''
    for opt, arg in opts:
        if opt in ['-a', '--all']:
            do_monitor = do_clean = True
        elif opt in ['-m', '--monitor']:
            do_monitor = True
        elif opt in ['-v', '--clean']:
            do_clean = True
        elif opt in ['-f', '--follow']:
            data = arg.split('/')
            board = data[3]
            thread = int(data[5])
            title = data[6] if len(data) >= 7 else ''
        elif opt in ['-d', '--debug']:
            do_debug = True

    if board and thread:
        add_thread(board, thread, com=title)

    if do_monitor:
        monitor()

    if do_clean:
        clean()

    if do_debug:
        show()

    sys.exit(0)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(-1)
