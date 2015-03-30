#! /usr/bin/env/python2

import serial
from time import sleep
import re

class RequestError(Exception): pass

class ADCSArduino():

    # decorator function that opens and closes port and does stuff
    def open_close_port(function, *args):
        def open_close(self, *args):
            self.open_arduino_port()
            function(self, *args)
            self.close_arduino_port()
        return open_close

    def __init__(self, pr='/dev/ttyACM0', br=9600):
        # per le arduino
        self.arduino = serial.Serial()
        self.arduino.port = pr
        self.arduino.baudrate = br
        # calibration algorithm

    def call_control(self, data):
        # call control algorithm
        pass

    def open_arduino_port(self):
        # opens the serial port if it is not already open
        if not self.arduino.isOpen():
            self.arduino.open()

    def close_arduino_port(self):
        # closes the serial port if it not already closed
        if self.arduino.isOpen():
            self.arduino.close()

    def activate(self):
        # starts up the adcs arduino for buisness
        # changes the attitude of the satellite to the desired pos and
        # then returns the attitude when it has finished
        #
        # call this method from the event queue 
        data = self.get_sensor_data()
        self.call_control(data)
        sleep(1) 
        current_list = [1,2,3,4]
        self.post_change(current_list)
        
    def _prep_request(self, typ):
        # tells the arduino when we want to send/recieve data so
        # that the arduino does not have to take continous sensor
        # readings
        #   param: typ : String, the type of request, 
        #       'get' for arduino -> python
        #       'post' for python -> arduino
        self.arduino.flush()
        if (typ == 'get'):
            self.arduino.write('g')
        elif (typ == 'post'):
            self.arduino.write('p')
        else:
            raise RequestError('invalid request type')

    def gen_dict(self, ard):
        data = {}
        # gets all elements and removes \n
        sens = ard.split('}')
        sens.pop()
            
        # required regexs
        preg = re.compile('photodiodes:[-0-9][^;]*')
        mxreg = re.compile('mag_x:[-0-9][^;]*')
        myreg = re.compile('mag_x:[-0-9][^;]*')

        for i in sens:
            on = re.search('[0-9]', i).group()
            p = re.search(preg, i).group().split(':')[1]
            mx = re.search(mxreg, i).group().split(':')[1]
            my = re.search(myreg, i).group().split(':')[1]

            data[on] = {}
            data[on]['photodiodes'] = float(p)
            data[on]['mag_x'] = float(mx)
            data[on]['mag_y'] = float(my)

        return data

    def get_sensor_data(self):
        self.open_arduino_port() 
        self._prep_request('get')
        sleep(1)
        data = self.gen_dict(self.arduino.readline())
        self.close_arduino_port()
        return data

    @open_close_port
    def post_change(self, dat):
        # posts needed change to the arduino
        #   param : dat : tuple, the desired change
        self._prep_request('post')             
        self.arduino.write(str(dat))
