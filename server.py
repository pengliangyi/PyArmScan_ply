# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from gevent.monkey import patch_all; patch_all()

import argparse
import Queue
from threading import Thread

from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request, send_file

from scanner import Scanner


app = Flask(__name__)
# app.debug = True

# 事件队列
events = Queue.Queue()

# 扫描器
scanner = Scanner(events)
scanner.async_handle_events()


def run_in_thread(target):
    t = Thread(target=target)
    t.start()


@app.route('/events', methods=['POST'])
def put_event():
    event = request.json['event']
    events.put(event)
    return ''


@app.route('/next_event', methods=['GET'])
def get_next_event():
    try:
        event = events.get(block=True, timeout=10)
    except Queue.Empty:
        event = ''
    return event


@app.route('/next_image', methods=['GET'])
def get_next_image():
    # Read image from DMA?
    return send_file('out.jpg', mimetype='image/jpeg')


@app.route('/commands', methods=['POST'])
def send_command():
    command = request.json['command']

    if command == 'boot':
        run_in_thread(scanner.boot)
    elif command == 'start':
        run_in_thread(scanner.start)
    else:
        return 'Unrecognized command: %s' % command, 400

    return 'OK'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='The host of server.')
    parser.add_argument('--port', help='The port of server.')
    args = parser.parse_args()

    server = WSGIServer((args.host, args.port), app)
    server.serve_forever()
