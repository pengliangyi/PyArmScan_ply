# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from gevent.monkey import patch_all; patch_all()

import Queue

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
    return send_file('out.jpg', mimetype='image/jpeg')


@app.route('/commands', methods=['POST'])
def send_command():
    command = request.json['command']

    if command == 'scan':
        scanner.scan()
    else:
        print('unrecognized command: %s' % command)

    return ''


if __name__ == '__main__':  
    server = WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()
