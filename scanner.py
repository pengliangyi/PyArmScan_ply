# -*- coding: utf-8 -*-

from threading import Thread
import time

from fireflyP import Pwm
from fireflyP import Gpio

from gpio import GPIO


class GPIOReader(object):
    """GPIO 状态读取类: 读状态,timeout 阻塞读事件."""

    def __init__(self, gpio_name):
        self._gpio = GPIO(gpio_name)
        self._gpio.set_input()

        self._value = None

    def read_value(self):
        return self._gpio.read()

    def read_edge(self, edge, timeout_ms):
        def callback(val):
            self._value = val

        self._gpio.wait(edge, timeout_ms, callback)
        return self._value


class GPIOAsyncHandler(object):
    """GPIO 事件异步处理类."""

    def __init__(self, gpio_name):
        self._gpio = GPIO(gpio_name)
        self._gpio.set_input()

    def callback(self, val):
        """子类需要覆盖该函数,用于执行真正的回调处理."""
        raise NotImplementedError()

    def handle(self, edge, timeout_ms):
        def handler():
            while True:
                self._gpio.wait(edge, timeout_ms, callback=self.callback)
        t = Thread(target=handler)
        t.start()


class PWMController(object):
    """电机控制类."""

    def __init__(self, gpio_name, pwm_name, mux):
        Gpio.init()
        self._gpio = Gpio(gpio_name)
        self._gpio.set_mux(mux)

        Pwm.init()
        self._pwm = Pwm(pwm_name)

    def set_config(self, freq, duty, wait_s):
        self._pwm.set_config(freq, duty)
        self._pwm.start()
        time.sleep(wait_s)
        self._pwm.stop()


if __name__ == '__main__':
    # PWMController example
    pwmc = PWMController('GPIO7A1', 'PWM1', mux=1)  # set pwm1 mux
    pwmc.set_config(1000000, 500000, wait_s=10)  # set PWM1: freq=1kHz, duty=50%

    # GPIOReader example
    gpio1 = GPIOReader('GPIO8A6')
    gpio1.read_value()  # read normal value
    gpio1.read_edge(GPIO.BOTH_EDGE, 60000)  # read event value, timeout: 60s

    # GPIOAsyncHandler example
    class GPIOKaZhiAsyncHandler(GPIOAsyncHandler):
        """卡纸的异步处理类"""
        def callback(self, val):
            print "callback: pin_level:{}".format(val)
            # Stop all operations
            # ...
    gpio2 = GPIOKaZhiAsyncHandler('GPIO8A7')
    gpio2.handle(GPIO.BOTH_EDGE, 60000)  # wait 60s for each loop
