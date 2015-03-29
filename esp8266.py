#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# https://github.com/espressif/esp8266_at/wiki/AT_Description

import logging
import re

logging.basicConfig(level=logging.DEBUG)

MAX_CIPSEND_BUFFER_SIZE = 2048

class ESP8266Exception(Exception):
  pass

class ESP8266ExceptionUnresolvable(Exception):
  pass

class ESP8266(object):
  _successResponse_list = ('ok', 'ready', 'no change', 'send ok')
  _unresolvableFailureResponse_list = ('error', 'type error', 'alreay connect')

  def __init__(self, serial):
    assert serial.isOpen(), "Need a connected pySerial object"
    self._serial = serial
    self.sendCmd('AT')

  def scanForAccessPoints(self):
    return self.sendCmd('AT+CWLAP')

  def connectToAccessPoint(self, ssid_str, password_str):
    current_ssid_str = self.getConnectedAccessPoint()
    if current_ssid_str == ssid_str:
      logging.info('Already connected to access point: {}'.format(ssid_str))
      return
    if current_ssid_str != '<NOT CONNECTED>':  
      self.disconnectFromAccessPoint()
    self.setDeviceMode(1)
    self.sendCmd('AT+CWJAP="' + ssid_str + '","' + password_str + '"')

  def disconnectFromAccessPoint(self):
    self.sendCmd('AT+CWQAP')

  def getConnectedAccessPoint(self):
    try:
      responseLines_list = self.sendCmd('AT+CWJAP?')
    except ESP8266ExceptionUnresolvable:
      return '<NOT CONNECTED>'
    else:
      m = re.match(r'\+CWJAP:"(.*)"', responseLines_list[0])
      return m.group(1)

  def setDeviceMode(self, deviceMode_int):
    '''1=client, 2=AP, 3=both'''
    currentDeviceMode_int = self.getDeviceMode()
    if currentDeviceMode_int != deviceMode_int:
      self.sendCmd('AT+CWMODE={}'.format(deviceMode_int))

  def getDeviceMode(self):
    responseLines_list = self.sendCmd('AT+CWMODE?')
    m = re.match(r'\+CWMODE:(\d)', responseLines_list[0])
    return int(m.group(1))

  def getIPAddress(self):
    responseLines_list = self.sendCmd('AT+CIFSR')
    return responseLines_list[0]

  def sendCmd(self, cmd, retries=3):
    for i in range(retries):
      try:
        return self._sendCmd(cmd)
      except ESP8266Exception:
        if i == retries - 1:
          raise

  def sendBuffer(self, protocol_str, host_str, port_int, buf):
    self.sendCmd('AT+CIPMUX=0')
    currentStatus_str, currentProtocol_str, currentHost_str, currentPort_int = self.getCipStatus()
    print currentStatus_str, currentProtocol_str, currentHost_str, currentPort_int
    if currentProtocol_str != protocol_str or currentHost_str != host_str or currentPort_int != port_int:
      if currentStatus_str in ('GOTIP', 'CONNECTED'):
        self.closeCip()
      self.startCip(protocol_str, host_str, port_int)
    while buf:
      self._sendBuffer(buf[:MAX_CIPSEND_BUFFER_SIZE])
      buf = buf[MAX_CIPSEND_BUFFER_SIZE:]

  def startCip(self, protocol_str, host_str, port_int):
    cmd = 'AT+CIPSTART="UDP","{}",{}'.format(host_str, port_int)
    self.sendCmd(cmd)

  def getCipStatus(self):
    responseLines_list = self._sendCmd('AT+CIPSTATUS')
    m = re.match(r'STATUS:(\d)', responseLines_list[0])
    status_int = int(m.group(1)) - 1
    status_str = ('<INVALID>', 'GOTIP', 'CONNECTED', 'DISCONNECTED', '<INVALID>')[status_int]
    protocol_str, host_str, port_int = None, None, None
    if len(responseLines_list) >= 2:
      m = re.match(r'\+CIPSTATUS:0,"(.+)","(.+)",(\d+),0', responseLines_list[1])
      if m:
        protocol_str, host_str, port_int = m.group(1), m.group(2), int(m.group(3))
    return status_str, protocol_str, host_str, port_int
    
  def closeCip(self):
    return self._sendCmd('AT+CIPCLOSE')
  
  #
  # Private.
  #

  def _sendCmd(self, cmd):
    self._sendStr(cmd)
    return self._getResponse()
      
  def _sendStr(self, s):  
    logging.debug('> %s' % s)
    self._serial.flushInput()
    self._serial.write(s + '\r\n')
    # eat echo
    self._serial.readline()
    
  def _getResponse(self):
    responseLines_list = []

    while True:
      r = self._serial.readline()
      if not r:
        raise ESP8266Exception('Timeout. Possible partial response: {}'.format(' / '.format(responseLines_list)))
      r = r.strip()
      if r:
        logging.debug('< {}'.format(r))
        responseLines_list.append(r)
        if (r.lower() in self._successResponse_list):
          return responseLines_list
        if (r.lower() in self._unresolvableFailureResponse_list):
          raise ESP8266ExceptionUnresolvable('Failed with unresolvable response: {}'.format(' / '.format(responseLines_list)))

    raise ESP8266Exception('Failed with unknown response: {}'.format(' / '.format(responseLines_list)))

  def _sendBuffer(self, s):
    assert len(s) <= MAX_CIPSEND_BUFFER_SIZE
    self._sendStr('AT+CIPSEND={}'.format(len(s)))
    # eat the send prompt ("> ")
    sendPrompt_str = self._serial.read(2)
    assert sendPrompt_str == '> '
    # send the buffer
    self._serial.write(s)
    return self._getResponse()
