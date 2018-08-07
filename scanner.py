# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

import helpers
from gpio import GPIO


class Scanner(object):

    def __init__(self, events):
        self._events = events

        # 机盖的 GPIO 端口
        self._jigai_gpio = helpers.GPIOReader.from_gpio_name('GPIO8A7')  # 参数待修改

        # 获取是否有纸的 GPIO 端口
        self._youzhi_gpio = helpers.GPIOReader.from_gpio_name('GPIO8A8')  # 参数待修改

        # 卡纸的 GPIO 端口
        self._kazhi_async_handler = helpers.GPIOAsyncHandler.from_gpio_name('GPIO8A6')  # 参数待修改
        # 马达 xx 端口
        self._motor_pwm1 = helpers.PWMController('GPIO7A1', 'PWM1', mux=1)  # 参数待修改

    def async_handle_events(self):
        """开启所有的事件异步处理器."""
        self._kazhi_async_handler.handle(GPIO.BOTH_EDGE, 60000, self.kazhi_callback)  # wait 60s for each loop

    def wait_papper_put(self):
        """阻塞等待放纸."""
        while True:
            val = self._youzhi_gpio.read_edge(GPIO.BOTH_EDGE, 10000)  # 每次读事件超时 10 秒,参数待修改
            if val == '表示有纸的 val':  # 有纸了,退出阻塞等待
                break

    def boot(self):
        """开机后的处理流程."""
        # 1. 判断是否合上机盖
        val = self._jigai_gpio.read_value()
        if val != '表示合上机盖的 val':
            self._events.put('提示 client 端合上机盖')
            return

        # 2. 已经合上机盖, 延时 0.15 秒
        time.sleep(0.15)

        # 3. 判断进纸口是否有纸
        val = self._youzhi_gpio.read_value()
        if val != '表示有纸的 val':
            # 4. 进行开机复位
            # ... 控制电机

            # 5. 阻塞等待有纸的事件
            self.wait_papper_put()

        # 5. 到这里,已经有纸了. 等待开始工作指令

    def start(self):
        """开始工作的指令."""
        # 1. 检测到开始信号. 怎么检测?

        # 2. 判断是否进纸口有纸
        val = self._youzhi_gpio.read_value()
        if val != '表示有纸的 val':
            # 3. 无纸报错
            self._events.put('提示 client 端无纸')

            # 4. 阻塞等待放纸
            self.wait_papper_put()

            # 5. 退出,*再次*等待开始工作指令
            return

        # 6. 上述第 2 步判断有纸, 判断纸道内是否有纸
        val = ''  # 读取纸道内是否有纸的 val
        if val == '表示纸道内有纸的 val':
            # 7. 提示卡纸错误
            self._events.put('提示 client 端卡纸')

        # 8. 没有卡纸,开始扫描
        self.scan()

    def scan(self):
        """发送启动扫描的指令."""

        # 按扫描中的各种流程,一步步判断操作

    def kazhi_callback(self, val):
        """卡纸的异步处理."""
        print('stop all operations...')
        self._motor_pwm1.set_config(1000000, 500000, wait_s=10)  # 参数待修改
