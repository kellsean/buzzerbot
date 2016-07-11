#!/usr/bin/python

import BaseHTTPServer
import SocketServer
import logging
import yaml
import cgi
import os
from RPIO import PWM
from time import sleep

stream = open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r')
config = yaml.load(stream)

port             = int(config['port'])
opto_gpio        = config['opto_gpio']
opto_press_time = float(config['opto_press_time'])
twilio_sid       = config['twilio_sid']
number_whitelist = config['number_whitelist']

rpio.setMode('physical');
var rpio = require('rpio');

/*
 * Set the initial state to low.  
 */
 
rpio.open(opto_gpio, rpio.OUTPUT, rpio.LOW);

class ServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_POST(self):
    logging.warning('-- got POST --')
    form = cgi.FieldStorage(
      fp = self.rfile,
      headers = self.headers,
      environ= {
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': self.headers['Content-Type'],
      }
    )
    
    sid = form.getvalue('AccountSid')
    if sid != twilio_sid:
      logging.warning('Incorrect Twilio Account SID')
      return
    logging.warning('SID looks good')

    number = form.getvalue("From")
    if number not in number_whitelist:
      logging.warning('access denied: number not recognized')
      return
    logging.warning('number is on whitelist, welcome home')

    command = form.getvalue('Body').lower()
    if command == 'open':
      logging.warning('opening door')
      rpio.write(opto_gpio, rpio.HIGH)
      sleep(opto_press_time)
      rpio.write(opto_gpio, rpio.LOW)
    else:
      logging.warning('command not found: ' + command)

Handler = ServerHandler
httpd = SocketServer.TCPServer(("", port), Handler)
httpd.serve_forever()
