#!/usr/bin/env python

import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 8989

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
  data, addr = sock.recvfrom(2048)
  print data
  print addr
  print
