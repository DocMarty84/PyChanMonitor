#!/usr/bin/env python
# coding: utf-8

import getopt
import logging
import logging.handlers
import os
import sys

from downloader import DownloaderBase

LOG_FILENAME = '..' + os.sep + 'pychanmonitor.log'

l = logging.getLogger(__name__)

def main(argv):
    try:
        opts, args = getopt.getopt(
            argv, "amvf:d", ["all", "monitor", "clean", "follow", "debug", "log="])

    except getopt.GetoptError:
        l.critical("Incorrect parameters. Exiting...")
        sys.exit(2)

    # Parse arguments
    do_monitor = do_debug = do_clean = False
    board = thread = ''
    loglevel = logging.INFO
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
        elif opt in ['--log']:
            loglevel_num = getattr(logging, arg.upper(), None)
            if isinstance(loglevel_num, int):
                loglevel = loglevel_num

    # Logging stuff
    f = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=5)
    fh.setLevel(loglevel)
    fh.setFormatter(f)
    sh = logging.StreamHandler()
    sh.setLevel(loglevel)
    sh.setFormatter(f)
    logging.basicConfig(level=loglevel, handlers=[fh, sh])

    down = DownloaderBase()
    if board and thread:
        down.add_thread(board, thread, com=title)

    if do_monitor:
        down.monitor()

    if do_clean:
        down.clean()

    if do_debug:
        down.show()

    sys.exit(0)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(-1)
