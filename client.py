# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import argparse
import signal
from io import BytesIO

import requests
from PIL import Image


class EventHandler(object):

    next_event_path = '/next_event'
    next_image_path = '/next_image'

    def __init__(self, base_url, timeout_s=10):
        self._next_event_url = base_url + self.next_event_path
        self._next_event_timeout_s = timeout_s
        self._next_image_url = base_url + self.next_image_path
        self._stop_flag = False

    def handle(self, event):
        print('[EVENT] %s' % event)
        if event == 'gen_image':
            resp = requests.get(self._next_image_url, timeout=self._next_event_timeout_s)
            img = Image.open(BytesIO(resp.content))
            print('[INFO] Got image: %s' % img)

    def listen(self):
        while not self._stop_flag:
            try:
                resp = requests.get(self._next_event_url, timeout=self._next_event_timeout_s)
            except requests.exceptions.Timeout:
                pass
            except Exception as exc:
                print(str(exc))
                break
            else:
                if resp.status_code == 200:
                    event = resp.text
                    if event:
                        self.handle(event)
                else:
                    print('resp error: code (%s), text (%s)' % (resp.status_code, resp.text))

    def stop(self):
        self._stop_flag = True
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='The host of server.')
    parser.add_argument('--port', help='The port of server.')
    args = parser.parse_args()

    base_url = 'http://%s:%s' % (args.host, args.port)
    handler = EventHandler(base_url)

    def sig_handler(signum, frame):
        print('user interrupted, exiting...')
        handler.stop()
    signal.signal(signal.SIGINT, sig_handler)

    handler.listen()
