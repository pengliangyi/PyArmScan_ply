# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from threading import Thread
import time

from fireflyP import Pwm
from fireflyP import Gpio

from gpio import GPIO

class MotorFreq(object):
    CUOZHI_FREQ = 10000000/16
    ZOUZHI_FREQ = CUOZHI_FREQ

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
        self._value = None
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
                val = self._gpio.read_edge(edge, timeout_ms)
                if val != None and callback != None:
                    callback(val)

        t = Thread(target=handler)
        t.start()


class SmartPwm(Pwm):
    """智能 Pwm."""

    instantiated = False
    _pwm1 = None
    _pwm3 = None

    def __new__(cls, *args, **kwargs):
        if not cls.instantiated:
            # 第一次实例化时, 自动调用 Pwm.init()
            Gpio.init()
            cls._pwm1 = Gpio('GPIO7A1')
            cls._pwm3 = Gpio('GPIO7C7')
            cls._pwm1.set_mux(1)
            cls._pwm3.set_mux(3)
            Pwm.init()
            cls.instantiated = True
        return object.__new__(cls, *args, **kwargs)


class MotorController(object):
    """电机控制类 v2."""
    FRONT_DIR = 1
    BACK_DIR = 0

    def __init__(self, pwm_args, dir_args, enable_args):
        """
        :param pwm_args: e.g. {'gpio_name': 'GPIO7A1', 'mux': 1, 'name': 'PWM1', 'freq': 'xx', 'duty': 'xx'}
        :param dir_args: e.g. {'name': 'GPIO8A4', 'write': 0}
        :param enable_args: e.g. {'name': 'GPIO8A7', 'write': 1}
        """
        self._pwm = SmartPwm(pwm_args['name'])
        self._pwm.set_config(pwm_args['freq'], pwm_args['freq']/2)

        self._dir = GPIO(dir_args['name'])
        self._dir.set_output()
        self._dir.write(dir_args['write'])

        self._enable = GPIO(enable_args['name'])
        self._enable.set_output()
        self._enable.write(enable_args['write'])

    def start(self):
        self._enable.write(0)
        self._pwm.start()

    def stop(self):
        self._pwm.stop()
        self._enable.write(1)

    def set_freq(self, freq):
        self._pwm.set_config(freq, freq/2)

    @property
    def dir(self):
        return self._dir.read()

    @dir.setter
    def dir(self, value):
        self._dir.write(value)

class ZouZhiMotor(object):
    def __init__(self):
        self._mc = MotorController({'name': 'PWM1', 'freq': MotorFreq.ZOUZHI_FREQ}, {'name': 'GPIO8A4', 'write': 1},{'name': 'GPIO8A7', 'write': 1})


    def start(self):
        self._mc.dir = MotorController.BACK_DIR
        self._mc.start()

    def speedup(self):
        self._mc.dir = MotorController.BACK_DIR
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ * 2)
        self._mc.start()
        time.sleep(0.2)
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ * 1.5)
        self._mc.start()
        time.sleep(0.15)
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ)
        self._mc.start()

    def stop(self):
        self._mc.stop()

class CuoZhiMotor(object):
    def __init__(self):
        self._mc = MotorController({'name': 'PWM3', 'freq': MotorFreq.CUOZHI_FREQ}, {'name': 'GPIO6B0', 'write': 0}, {'name': 'GPIO5C0', 'write': 1})
        self._mc.dir = MotorController.FRONT_DIR

    def start(self):
        self._mc.start()

    def speedup(self):
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ * 2)
        self._mc.start()
        time.sleep(0.2)
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ * 3 / 4)
        self._mc.start()
        time.sleep(0.15)
        self._mc.set_freq(MotorFreq.ZOUZHI_FREQ * 2 / 3)
        self._mc.start()

    def reset(self):
        self._mc.start()
        time.sleep(0.5)
        self._mc.stop()
        self._mc.dir = MotorController.BACK_DIR
        self._mc.start()
        time.sleep(0.06)
        self._mc.stop()
        self._mc.dir = MotorController.FRONT_DIR

    def stop(self):
        self._mc.stop()

class DoubleSensor(object):
    @property
    def result(self):
        return 0

    def start(self):
        pass

    def stop(self):
        pass

class Capture(object):
    def __init__(self):
        pass

    def acquier(self):
        pass


if __name__ == '__main__':
    # PWMController example
    # pwmc = PWMController('GPIO7A1', 'PWM1', mux=1)  # set pwm1 mux
    # pwmc.set_config(1000000, 500000, wait_s=10)  # set PWM1: freq=1kHz, duty=50%
    # 第一次实例化时, 自动调用 Pwm.init()
    mc = CuoZhiMotor()
    mc.reset()
    time.sleep(1)
    mc.stop()


