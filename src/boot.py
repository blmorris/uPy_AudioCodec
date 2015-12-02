# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

import pyb
#pyb.main('main.py') # main script to run after this one
#pyb.usb_mode('CDC+MSC') # act as a serial and a storage device
#pyb.usb_mode('CDC+HID') # act as a serial device and a mouse

# Config for rapid C dev, DFU and debug
# Use USB port only for DFU and power
pyb.usb_mode(None)
# Configure REPL to use UART (and outside USB / Serial adapter)
# uart = pyb.UART(4, 9600)
uart = pyb.UART(4, 115200)
pyb.repl_uart(uart)
