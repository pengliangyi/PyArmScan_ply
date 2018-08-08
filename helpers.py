# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from threading import Thread
import time

from fireflyP import Pwm
from fireflyP import Gpio

from gpio import GPIO


class GPIOReader(object):
    """GPIO 状态读取类: 读状态,timeout 阻塞读事件."""

    def __init__(self, gpio):
        self._gpio = gpio
        self._value = None

    @classmethod
    def from_gpio_name(cls, name):
        _gpio = GPIO(name)
        _gpio.set_input()
        return cls(_gpio)

    def read_value(self):
        return self._gpio.read()

    def read_edge(self, edge, timeout_ms):
        def callback(val):
            self._value = val

        self._gpio.wait(edge, timeout_ms, callback)
        return self._value


class GPIOAsyncHandler(object):
    """GPIO 事件异步处理类."""

    def __init__(self, gpio):
        self._gpio = gpio

    @classmethod
    def from_gpio_name(cls, name):
        _gpio = GPIO(name)
        _gpio.set_input()
        return cls(_gpio)

    def handle(self, edge, timeout_ms, callback):
        def handler():
            while True:
                self._gpio.wait(edge, timeout_ms, callback=callback)
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


class SmartGpio(Gpio):
    """智能 Gpio."""

    instantiated = False

    def __new__(cls, *args, **kwargs):
        if not cls.instantiated:
            # 第一次实例化时, 自动调用 Gpio.init()
            Gpio.init()
            cls.instantiated = True
        return object.__new__(cls, *args, **kwargs)


class SmartPwm(Pwm):
    """智能 Pwm."""

    instantiated = False

    def __new__(cls, *args, **kwargs):
        if not cls.instantiated:
            # 第一次实例化时, 自动调用 Pwm.init()
            Gpio.init()
            cls.instantiated = True
        return object.__new__(cls, *args, **kwargs)


class MotorController(object):
    """电机控制类 v2."""

    def __init__(self, pwm_args, dir_args, enable_args):
        """
        :param pwm_args: e.g. {'gpio_name': 'GPIO7A1', 'mux': 1, 'name': 'PWM1', 'freq': 'xx', 'duty': 'xx'}
        :param dir_args: e.g. {'name': 'GPIO8A4', 'write': 0}
        :param enable_args: e.g. {'name': 'GPIO8A7', 'write': 1}
        """
        self._gpio = SmartGpio(pwm_args['gpio_name'])
        self._gpio.set_mux(pwm_args['mux'])

        self._pwm = SmartPwm(pwm_args['name'])
        self._pwm.set_config(pwm_args['freq'], pwm_args['duty'])

        self._dir = GPIO(dir_args['name'])
        self._dir.set_output()
        self._dir.write(dir_args['write'])

        self._enable = GPIO(enable_args['name'])
        self._enable.set_output()
        self._enable.write(enable_args['write'])


if __name__ == '__main__':
    # PWMController example
    pwmc = PWMController('GPIO7A1', 'PWM1', mux=1)  # set pwm1 mux
    pwmc.set_config(1000000, 500000, wait_s=10)  # set PWM1: freq=1kHz, duty=50%

    # GPIOReader example
    gpio1 = GPIO('GPIO8A6')
    gpio1.set_input()

    gpio_reader1 = GPIOReader(gpio1)
    gpio_reader1.read_value()  # read normal value
    gpio_reader1.read_edge(GPIO.BOTH_EDGE, 60000)  # read event value, timeout: 60s

    # GPIOAsyncHandler example
    def callback(self, val):
        """卡纸的异步处理类"""
        print('callback: pin_level:{}'.format(val))
        # Stop all operations
        # ...
    gpio2 = GPIO('GPIO8A7')
    gpio2.set_input()
    gpio_reader2 = GPIOAsyncHandler(gpio2)
    gpio_reader2.handle(GPIO.BOTH_EDGE, 60000, callback)  # wait 60s for each loop
