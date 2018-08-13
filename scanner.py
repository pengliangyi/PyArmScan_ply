# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import helpers
from gpio import GPIO
from helpers import MotorController, GPIOReader

class Scanner(object):

    NoPaper = 0
    HasPaper = 1
    Freq = 10000000/16

    def __init__(self, events):
        self._events = events
        # 马达 xx 端口
        self._motor_zouzhi = helpers.MotorController({'name': 'PWM1', 'freq': Scanner.Freq}, {'name': 'GPIO8A4', 'write': 0},{'name': 'GPIO8A7', 'write': 1})  # 参数待修改
        # 马达 走纸 端口
        self._motor_cuozhi = helpers.MotorController({'name': 'PWM3', 'freq': Scanner.Freq*1.4}, {'name': 'GPIO6B0', 'write': 0}, {'name': 'GPIO5C0', 'write': 1})

        # 机盖的 GPIO 端口
        self._jigai_gpio = helpers.GPIOReader.from_gpio_name('GPIO5B6')  # 参数待修改

        # 获取是否有纸的 GPIO 端口
        self._youzhi_gpio = helpers.GPIOReader.from_gpio_name('GPIO5B5')  # 参数待修改

        #卡纸的GPIO端口
        self._kazhi_gpio = helpers.GPIOReader.from_gpio_name("GPIO5B4")

        # 开盖的 GPIO 端口管理者

        self._kaigai_async_handler = helpers.GPIOAsyncHandler(self._jigai_gpio)



    def async_handle_events(self):
        """开启所有的事件异步处理器."""
        self._kaigai_async_handler.handle(GPIO.BOTH_EDGE, 60000, self.kazhi_callback)  # wait 60s for each loop

    def wait_papper_put(self):
        """阻塞等待放纸."""
        print '阻塞'
        while True:
            val = self._youzhi_gpio.read_edge(GPIO.BOTH_EDGE, 10000)  # 每次读事件超时 10 秒,参数待修改
            if val == '表示有纸的 val':  # 有纸了,退出阻塞等待
                break

    def boot(self):
        """开机后的处理流程."""
        # 1. 判断是否合上机盖
        val = self._jigai_gpio.read_value()
        if val != 0:#'表示合上机盖的 val':
            self._events.put('提示 client 端合上机盖')
            print '提示 client 端合上机盖'
            self.stop()
            return

        # 2. 已经合上机盖, 延时 0.15 秒
        time.sleep(0.15)

        # 3. 判断进纸口是否有纸
        val = self._kazhi_gpio.read_value()
        if val == Scanner.HasPaper:  # '表示有纸的 val':
            print '纸道有纸'
            self._events.put('提示 client 纸道有纸，卡纸')

        val = self._youzhi_gpio.read_value()
        if val == Scanner.NoPaper: #'表示有纸的 val':
            # 4. 进行开机复位
            # ... 控制电机
            self._motor_cuozhi.dir = self._motor_cuozhi.Front_Dir
            self._motor_cuozhi.start()
            time.sleep(2)
            self._motor_cuozhi.stop()
            self._motor_cuozhi.dir = self._motor_cuozhi.Back_Dir
            self._motor_cuozhi.start()
            time.sleep(2)
            self._motor_cuozhi.stop()


            # 5. 阻塞等待有纸的事件
            #self.wait_papper_put()

        # 5. 到这里,已经有纸了. 等待开始工作指令

    def start(self):
        """开始工作的指令."""
        # 1. 检测到开始信号. 怎么检测?
        print 'in start'

        # 2.判断纸道内是否有纸
        val = self._kazhi_gpio.read_value()
        if val != self.NoPaper:
            # 3. 无纸报错
            print '提示 client 端卡纸'
            self._events.put('提示 client 端卡纸')
            return


        # 4. 阻塞等待放纸
        #self.wait_papper_put()

        # 5. 退出,*再次*等待开始工作指令


        # 6. 上述第 2 步判断有纸, 判断纸道内是否有纸
        val = self._youzhi_gpio.read_value()  #判断是否进纸口有纸
        if val == self.NoPaper:#'表示纸道内有纸的 val':
            # 7. 提示卡纸错误
            print '提示 client 端无纸'
            self._events.put('提示 client 端无纸')
            return

        # 8. 没有卡纸,开始扫描
        self.scan()

    def scan(self):
        """发送启动扫描的指令."""
        print 'scan'
        self._motor_cuozhi.dir = self._motor_cuozhi.Front_Dir
        self._motor_zouzhi.start()
        print 'motor main start'
        while True:
            val = self._youzhi_gpio.read_value()
            if val == self.HasPaper:            #有纸
                print 'has paper, cou zhi start'
                self._motor_cuozhi.start()
                print 'wait rising'
                val = self._kazhi_gpio.read_edge(GPIO.RISING_EDGE, 2000)
                if val != None: #正常触发
                    print 'paper in, cou zhi stop'
                    self._events.put('gen_image')
                    self._motor_cuozhi.stop()
                else:
                    print 'cuo zhi error'
                    self.kazhi_callback(3)
                    return

                val = self._kazhi_gpio.read_edge(GPIO.FALLING_EDGE, 2000)
                if val != None: #正常纸张离开
                    print 'paper out'
                    # 触发采集 待添加
                else:
                    print 'paper jum'
                    self.kazhi_callback(3)
                    return
            else:
                time.sleep(0.1)
                print 'paper out, stop'
                self.stop()
                return


        # 按扫描中的各种流程,一步步判断操作

    def kazhi_callback(self, val):
        """卡纸的异步处理."""
        print('stop all operations...')
        self._motor_zouzhi.stop()
        self._motor_cuozhi.stop()
        self._events.put('异常停止')



    def test(self):
        motor_Main = self._motor_zouzhi
        motor_Main.dir = MotorController.Back_Dir
        motor_Main.start()

        motor_feeding = self._motor_cuozhi
        motor_feeding.dir = MotorController.Front_Dir
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
        self._motor_cuozhi.stop()
        self._motor_zouzhi.stop()