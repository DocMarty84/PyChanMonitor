#!/usr/bin/env python
# coding: utf-8

from base.downloader import DownloaderBase

import getopt
import logging as l
import sys

l.basicConfig(level=l.DEBUG)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "amvf:d", ["all", "monitor", "clean", "follow", "debug"])

    except getopt.GetoptError:
        l.critical("Incorrect parameters. Exiting...")
        sys.exit(2)

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
