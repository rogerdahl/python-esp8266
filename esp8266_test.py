#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import logging
import serial

logging.basicConfig(level=logging.DEBUG)

import esp8266

# ESP8266 serial port.
port = '/dev/ttyAMA0' # AMA is a Raspberry Pi thing.
speed = 9600
timeout = 10

# WiFi connection.
ssid = 'NSA'
pwd = 'wifi-password'

# Open connection.
serial_connection = serial.Serial(port, speed, timeout=timeout)
serial_connection.open()

# Connect to the access point. Get IP address via DHCP.
esp = esp8266.ESP8266(serial_connection)
esp.connectToAccessPoint(ssid, pwd)
ip_address = esp.getIPAddress()
print 'My IP: {}'.format(ip_address)

# Create a buffer with test data.
buf += 'A' * 2047
buf += 'B'
buf += 'C' * 2047
buf += 'D'
buf += 'E' * 5

# UDP broadcast the test data.
esp.sendBuffer('UDP', '192.168.1.255', 8989, buf)

# Close connection.
serial_connection.close()
