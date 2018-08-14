# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import helpers
from gpio import GPIO
from threading import Thread, Event
from helpers import MotorController, GPIOReader, DoubleSensor

def run_in_thread(target):
    t = Thread(target=target)
    t.start()

class Scanner(object):

    NO_PAPER = 0
    HAS_PAPER = 1
    PANEL_CLOSED = 0
    PANEL_OPEN = 1
    FREQ = 10000000/16

    def __init__(self, events):
        self._events = events
        # 马达 xx 端口
        self._motor_zouzhi = helpers.ZouZhiMotor() # 参数待修改
        # 马达 走纸 端口
        self._motor_cuozhi = helpers.CuoZhiMotor()

        # 机盖的 GPIO 端口
        self._jigai_gpio = helpers.GPIOReader.from_gpio_name('GPIO5B6')  # 参数待修改

        # 获取是否有纸的 GPIO 端口
        self._youzhi_gpio = helpers.GPIOReader.from_gpio_name('GPIO5B5')  # 参数待修改

        #卡纸的GPIO端口
        self._kazhi_gpio = helpers.GPIOReader.from_gpio_name("GPIO5B4")

        # 开盖的 GPIO 端口管理者
        self._kaigai_async_handler = helpers.GPIOAsyncHandler(self._jigai_gpio)

        # 双张检测传感器
        self._double_sensor = DoubleSensor()

        #图像采集
        self._capture = helpers.Capture()

        self._scan_event = Event()
        self._scan_event.set()
        self._stop_flag = False

    @property
    def scan_flag(self):
        return self._scan_event.is_set()

    def async_handle_events(self):
        """开启所有的事件异步处理器."""
        self._kaigai_async_handler.handle(GPIO.RISING_EDGE, 60000, self.kazhi_callback)  # wait 60s for each loop
        self._kaigai_async_handler.handle(GPIO.FALLING_EDGE, 60000, self.boot_callback)  # wait 60s for each loop

    def wait_papper_put(self):
        """阻塞等待放纸."""
        print '阻塞'
        while True:
            val = self._youzhi_gpio.read_edge(GPIO.BOTH_EDGE, 10000)  # 每次读事件超时 10 秒,参数待修改
            if val == '表示有纸的 val':  # 有纸了,退出阻塞等待
                break

    def boot(self):
        """开机后的初始化处理流程."""
        # 1. 判断是否合上机盖
        val = self._jigai_gpio.read_value()
        if val != Scanner.PANEL_CLOSED:#'表示合上机盖的 val':
            self._events.put('提示 client 端合上机盖')
            self.stop()
            print "机盖未关闭，请合上机盖"  # test print
            return

        # 2. 已经合上机盖, 延时 0.15 秒
        time.sleep(0.15)

        # 3. 判断纸道是否有纸
        val = self._kazhi_gpio.read_value()
        if val == Scanner.HAS_PAPER:  # '表示有纸的 val':
            self._events.put('提示 client 纸道有纸，卡纸')
            print "纸道有纸，请打开机盖清理纸张" #test print
            return

        # 4. 判断入纸口是否有纸
        val = self._youzhi_gpio.read_value()
        if val == Scanner.NO_PAPER: #'表示无纸的 val':
           # 进纸口无纸，进行搓纸轮复位
            self._motor_cuozhi.reset()
            # ... 控制电机

            # 5. 阻塞等待有纸的事件
            #self.wait_papper_put()

        # 5. 到这里,已经有纸了. 等待开始工作指令
            print "请放纸"  # test print
        else:
            print "等待启动扫描"  # test print

    def start(self):
        """开始工作的指令."""
        # 1. 检测到开始信号. 怎么检测?

        # 2.判断纸道内是否有纸
        val = self._kazhi_gpio.read_value()
        if val != Scanner.NO_PAPER:
            # 3. 有纸报错
            self._events.put('提示 client 端卡纸')
            print "纸道有纸，请打开机盖清理纸张"  # test print
            return


        # 4. 阻塞等待放纸
        #self.wait_papper_put()

        # 5. 退出,*再次*等待开始工作指令


        # 6. 上述第 2 步判断有纸, 判断入纸口是否有纸
        val = self._youzhi_gpio.read_value()  #判断入纸口是否有纸
        if val == self.NO_PAPER:#'表示入纸口无纸的 val':
            # 7. 提示无纸
            self._events.put('提示 client 端无纸')
            print "无纸，请放纸"  # test print
            return

        # 8. 开始扫描
        if  self._scan_event.is_set():
            self._scan_event.clear()
            run_in_thread(self._scan)
            #self._scan()

    def _scan(self):
        self._scan_loop()
        self._scan_event.set()

    def _scan_loop(self):
        """发送启动扫描的指令."""
        self._motor_zouzhi.speedup()
        while True:
            val = self._youzhi_gpio.read_value()
            if val == self.HAS_PAPER:            #有纸
                self._motor_cuozhi.start()
                val = self._kazhi_gpio.read_edge(GPIO.RISING_EDGE, 2000)
                if val != None: #正常触发
                    self._events.put('gen_image')
                    self._capture.acquier()
                    self._motor_cuozhi.stop()
                    self._double_sensor.start()
                else:
                    self.kazhi_callback(3)
                    return

                val = self._kazhi_gpio.read_edge(GPIO.FALLING_EDGE, 2000)
                if val != None: #正常纸张离开
                    if self._double_sensor.result != 0:
                        self._events.put('双张入纸')
                    # 触发采集 待添加
                else:
                    self.kazhi_callback(3)
                    return
            else:
                time.sleep(0.1)
                self.stop()
                return


        # 按扫描中的各种流程,一步步判断操作

    def kazhi_callback(self, val):
        """卡纸的异步处理."""
        print('stop all operations...')
        self._motor_zouzhi.stop()
        self._motor_cuozhi.stop()
        self._events.put('异常停止')

    def boot_callback(self, val):
        self.boot()

    def test(self):
        motor_Main = self._motor_zouzhi
        motor_Main.dir = MotorController.BACK_DIR
        motor_Main.start()

        motor_feeding = self._motor_cuozhi
        motor_feeding.dir = MotorController.FRONT_DIR
        motor_feeding.start()

        gpio_reader1 = self._kazhi_gpio
        val = gpio_reader1.read_value()  # read normal value
        val = gpio_reader1.read_edge(GPIO.RISING_EDGE, 20000)
        if val is None:  # read event value, timeout: 60s
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

    def stop(self):
        self._stop_flag = True
        time.sleep(0.05)
        self._motor_cuozhi.stop()
        self._motor_zouzhi.stop()
        self._scan_event.wait(1)
        self.boot()

if __name__ == '__main__':
        # PWMController example
        # pwmc = PWMController('GPIO7A1', 'PWM1', mux=1)  # set pwm1 mux
        # pwmc.set_config(1000000, 500000, wait_s=10)  # set PWM1: freq=1kHz, duty=50%
        # 第一次实例化时, 自动调用 Pwm.init()
        # 事件队列
    import Queue
    events = Queue.Queue()
    # 扫描器
    scanner = Scanner(events)
    scanner.boot()
    scanner.start()