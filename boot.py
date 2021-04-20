# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
# esp.osdebug(None)
import uos
import machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl
import time
import network

webrepl.start()
gc.collect()
gc.mem_free()
SSID = "MYSSID"
pswd = "MYPSWD"

sta_if = network.WLAN(network.STA_IF)

sta_if.active(True)
sta_if.connect(SSID, pswd)
while not sta_if.isconnected():
    pass

print('Connection Successful')
print(sta_if.ifconfig())
