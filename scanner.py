# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import helpers
from gpio import GPIO


gpio_name_map = {
    'papper': 'GPIO8A6',  # 参数待修改
}


class Scanner(object):

    def __init__(self, events):
        self._events = events

        # 机盖的 GPIO 端口
        self._jigai_gpio = helpers.GPIOReader.from_gpio_name('GPIO8A7')

        # 卡纸的 GPIO 端口
        self._kazhi_async_handler = helpers.GPIOAsyncHandler.from_gpio_name(gpio_name_map['papper'])
        # 马达 xx 端口
        self._motor_pwm1 = helpers.PWMController('GPIO7A1', 'PWM1', mux=1)  # 参数待修改

    def async_handle_events(self):
        """开启所有的事件异步处理器."""
        self._kazhi_async_handler.handle(GPIO.BOTH_EDGE, 60000, self.kazhi_callback)  # wait 60s for each loop

    def scan(self):
        # 1. 判断是否合上机盖
        val = self._jigai_gpio.read_value()
        if val != '合上机盖的 val':
            self._events.put('合上机盖')

        print('start to scan')

    def kazhi_callback(self, val):
        """卡纸的异步处理."""
        print('stop all operations...')
        self._motor_pwm1.set_config(1000000, 500000, wait_s=10)  # 参数待修改
