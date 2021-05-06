from oscpy.server import OSCThreadServer
from time import sleep

def printer(values):
    print("here1")
    print(values)
def receive_values_from_max(ip,port):
  while(1):
    osc = OSCThreadServer()
    sock = osc.listen(address = ip,port = port, default = True)
    osc.bind(b'/density',printer)
    osc.bind(b'/cluster',printer)
    osc.bind(b"/mob_speed",printer)
    sleep(1000)
    osc.stop()
    return True
while(1):
    batch = receive_values_from_max('192.168.0.48',8001)
