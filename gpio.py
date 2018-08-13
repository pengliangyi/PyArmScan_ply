# -*- coding: utf-8 -*-

import os
import select
import re


class GPIO(object):
    _rpName = re.compile("GPIO(?P<chip>[0-8])(?P<bank>[A-D])(?P<offset>[0-7])")
    _gpio_base = r"/sys/class/gpio"
    _export = os.path.join(_gpio_base, "export")
    _unexport = os.path.join(_gpio_base, "unexport")
    
    _id_base = {
        '0' : 0,
        '1' : 24,
        '2' : 56,
        '3' : 88,
        '4' : 120,
        '5' : 152,
        '6' : 184,
        '7' : 216,
        '8' : 248
    }

    LOW  = 0
    HIGH = 1
    OUT  = "out"
    IN   = 'in' 
    BOTH_EDGE = 'both'
    RISING_EDGE = 'rising'
    FALLING_EDGE = 'falling'


    def __init__(self, gpioName):
        '''
        gpioName - For example: GPIO8A7
        '''
        self.name = gpioName.upper()
        self.id = self._name2id(self.name)

        self.fbase = os.path.join(self._gpio_base, 'gpio'+self.id)
        self.fvalue = os.path.join(self.fbase, 'value')
        self.fdirection = os.path.join(self.fbase, 'direction')
        self.fedge = os.path.join(self.fbase, 'edge')

        if not os.path.isdir(self.fbase):
            with open(self._export, 'w') as f:
                f.write(self.id)

        if not os.path.isdir(self.fbase):
            raise OSError("Cant create gpio file for: {} - id:{}".format(self.name, self.id)) 

        self.value = None

    @classmethod
    def destroy(cls, _id):
        with open(cls._unexport, 'w') as f:
            f.write(str(_id))

    @classmethod
    def _name2id(cls, name):
        result = cls._rpName.search(name)
        if result is not None:
            chip = result.group('chip')
            bank = result.group('bank')
            offset = int(result.group('offset'), 10)
        else:
            raise ValueError("Invalid GPIO Name: {}".format(self.name))\
        
        _id = cls._id_base[chip] + (ord(bank) - ord('A')) * 8 + offset
        return str(_id)
        

    def set_output(self):
        self._write_file(self.fdirection, self.OUT)
        if self.value is not None:
            self.value.close()
        self.value = open(self.fvalue, "w")


    def set_input(self):
        self._write_file(self.fdirection, self.IN)
        if self.value is not None:
            self.value.close()
        self.value = open(self.fvalue, "r")


    def set_edge(self, edge):
        self._write_file(self.fedge, edge)


    def set_drv(self):
        pass


    def write(self, level):
        _val = '0' if level is 0 else '1'
        if self.value is not None:
            self.value.write(_val)
            self.value.flush()


    def read(self):
        if self.value is not None:
            self.value.seek(0)
            val = self.value.read()
        return int(val, 10)


    def _read_file(self, fname):
        val = ''
        with open(fname, 'r') as f:
            f.seek(0)
            _strval = f.read()
            val = _strval.strip('\n')
        return val


    def _write_file(self, fname, val):
        with open(fname, 'w') as f:
            f.write(val)


    def wait(self, edge, timeout_ms=None, callback=None):
        direction = self._read_file(self.fdirection).strip("\n")
        if direction == self.OUT:
            print "GPIO must be input"
            return -1

        self._write_file(self.fedge, edge)

        po = select.poll()
        po.register(self.value, select.POLLPRI)

        self.read()
        events = po.poll(timeout_ms)
        if not events:
            print "timeout"
            return 1
        else:
            val = self.read()
            if callback is not None:
                callback(val)
            else:
                print "pin level: {}".format(val)
            return 0

    def __del__(self):
        if self.value is not None:
            self.value.close()


if __name__ == '__main__':
    import sys

    def interrupt_callback(pin_level):
        print "callback: pin_level:{}".format(pin_level) 
    
    def interrupt_test():
        print "GPIO Input Interrupt test..."
        inp = GPIO("GPIO8A6")
        inp.set_input()
        print "Current level: {}".format(inp.read())

        while True:
            inp.wait(inp.BOTH_EDGE, 60000, callback=interrupt_callback)
    
    def in_test():
        print "GPIO Input test..."
        inp = GPIO("GPIO8A6")
        inp.set_input()

        while True:
            val = inp.read()
            print "Input Level: {}".format(val)

        

    def out_test():
        print "GPIO Output test..."
        outp = GPIO("GPIO8A7")
        outp.set_output()
        while True:
            level = raw_input("Input the output level [0|1]:")
            level = level.strip(" ").strip("\n")
            level = int(level[0])
            level = 0 if level is 0 else 1
            outp.write(level)


    if len(sys.argv) == 2 and sys.argv[1].lower() == "in":
        in_test()

    elif len(sys.argv) == 2 and sys.argv[1].lower() == "out":
        out_test()

    elif len(sys.argv) == 2 and sys.argv[1].lower() == "interrupt":
        interrupt_test()

    else:
        print "Usage:\n python gpio.py [in|out|interrupt]"

    

