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
    Front_Dir = 1
    Back_Dir = 0

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

if __name__ == '__main__':
    # PWMController example
    # pwmc = PWMController('GPIO7A1', 'PWM1', mux=1)  # set pwm1 mux
    # pwmc.set_config(1000000, 500000, wait_s=10)  # set PWM1: freq=1kHz, duty=50%
    # 第一次实例化时, 自动调用 Pwm.init()

    motor_Main =  MotorController({'name': 'PWM1', 'freq': 1000000}, {'name': 'GPIO8A4', 'write': 0},{'name': 'GPIO8A7', 'write': 1})  # 参数待修改
    motor_Main.dir = MotorController.Back_Dir
    motor_Main.start()
    #time.sleep(5)
    # motor_Main.stop()
    # motor_Main.dir = MotorController.Back_Dir
    # motor_Main.start()
    # time.sleep(5)
    # motor_Main.stop()
    #
    motor_feeding = MotorController({'name': 'PWM3', 'freq': 1000000},{'name': 'GPIO6B0', 'write': 0},{'name': 'GPIO5C0', 'write': 1})  # 参数待修改
    motor_feeding.dir = MotorController.Front_Dir
    motor_feeding.start()
    # time.sleep(5)
    # motor_feeding.stop()
    # motor_feeding.dir = MotorController.Back_Dir
    # motor_feeding.start()
    # time.sleep(5)
    # motor_feeding.stop()

    # GPIOReader example

    gpio_reader1 = GPIOReader.from_gpio_name('GPIO5B4')
    val = gpio_reader1.read_value()  # read normal value
    val = gpio_reader1.read_edge(GPIO.RISING_EDGE, 20000)
    if  val is None:  # read event value, timeout: 60s
        print 'time out'
    elif val == 1:
        print 'raising'
    else:
        print 'failing'

    val = gpio_reader1.read_edge(GPIO.FALLING_EDGE, 20000)
    if val is None:  # read event value, timeout: 60s
        print 'time out'
    elif val == 1:
        print 'raising'
    else:
        print 'failing'

    motor_Main.stop()
    motor_feeding.stop()

    # # GPIOAsyncHandler example
    # def callback(self, val):
    #     """卡纸的异步处理类"""
    #     print('callback: pin_level:{}'.format(val))
    #     # Stop all operations
    #     # ...
    # gpio2 = GPIO('GPIO8A7')
    # gpio2.set_input()
    # gpio_reader2 = GPIOAsyncHandler(gpio2)
    # gpio_reader2.handle(GPIO.BOTH_EDGE, 60000, callback)  # wait 60s for each loop
