# -*- coding: utf-8 -*-

from time import sleep
import Queue

from gevent.monkey import patch_all; patch_all()  
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
# app.debug = True


events = Queue.Queue()


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
        print('start to scan')
    else:
        print('unrecognized command: %s' % command)

    return ''


if __name__ == '__main__':  
    server = WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()
