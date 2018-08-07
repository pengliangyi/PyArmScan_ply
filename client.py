# -*- coding: utf-8 -*-

import signal
import sys
import requests
import time
from io import BytesIO
from threading import Thread

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
        print('\nEVENT: %s' % event)
        if event == 'gen_image':
            resp = requests.get(self._next_image_url, timeout=self._next_event_timeout_s)
            img = Image.open(BytesIO(resp.content))
            print('Got image: %s' % img)

    def listen(self):
        while not self._stop_flag:
            try:
                resp = requests.get(self._next_event_url, timeout=self._next_event_timeout_s)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
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

    def start(self):
        t = Thread(target=self.listen)
        t.start()

    def stop(self):
        self._stop_flag = True


class Interaction(object):

    command_path = '/commands'

    def __init__(self, handler, base_url):
        self._handler = handler
        self._url = base_url + self.command_path

    def handle(self, cmd):
        resp = requests.post(self._url, json=dict(command=cmd))
        if resp.status_code == 200:
            print('OK')
        else:
            print('ERR: send cmd %r' % cmd)

    def run(self):
        while True:
            cmd = raw_input('cmd> ')
            if cmd == 'exit':
                self._handler.stop()
                break
            else:
                self.handle(cmd)
    

if __name__ == '__main__':
    base_url = 'http://localhost:5000'
    handler = EventHandler(base_url)
    handler.start()

    def sig_handler(signum, frame):
        print('user interrupted')
        handler.stop()
    signal.signal(signal.SIGINT, sig_handler)

    inter = Interaction(handler, base_url)
    inter.run()
