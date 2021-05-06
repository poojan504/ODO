"""Code to send data to Max"""
import socket
import sys
import json
from pythonosc import udp_client #need to install this in the system "pip install python-osc"
# Create a UDP socket

def send_data_to_max(tag,message,ip,port):
    try:
        client = udp_client.SimpleUDPClient("192.168.0.48", 8000)
        client.send_message(tag, message)
    finally:
        return True

tag = "/crowd_pos" #sample tag
message = "1.0,2,3,4,5,6,7,8,9,10" #sample message
ip = "192.168.0.48" #sample ip
port = 8000 #sample port
for i in range(5):
    send_data_to_max(tag,message,ip,port) #sample call
