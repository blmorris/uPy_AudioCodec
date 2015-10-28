import pyb
pot = pyb.ADC('Y12')
hpctl = pyb.Pin('Y11')
hpctl.init(hpctl.OUT_PP)
hpctl.high()
i2c = pyb.I2C(2)
i2c.init(i2c.MASTER)
# Might do a 'try' here to make sure both i2c devices are working:
i2c.scan()
#> [26, 96]

# Set Headphone Amp chip registers:
i2c.mem_write(0xc0, 96, 1) # control register: enable both amplifier channels, activate stereo mode
i2c.mem_write(0x35, 96, 2) # volume register; unmute both channels, set gain to ~0dB
i2c.mem_write(0x00, 96, 3) # output tri-state register; set both channels to output mode

# Set codec registers:
# THe SSM2604 uses a register addressing scheme that does not map directly to the uPy
# mem_read / mem_write methods.
# There are a total of 11 9-bit registers (R0-R9 and R15) which are selected using a
# 7-bit address. Register writes are constructed using the 'send' method:
# i2c.send('0b<7-bit register address><9-bit register data>', 26)
# Register reads can use 'mem_read' but the register address must be multiplied by 2
# (or shifted 1 bit left, so the 7-bit address is left justified)
# The read should be for two bytes, and the 'bytes' object that is returned will be
# two bytes long with the LSB first

# Set up Codec for Pass-Through
i2c.send(b'\x00\x17', 26) # LEFT ADC INPUT GAIN, ADDRESS 0x00: unmute left ADC, input gain=0dB
i2c.send(b'\x02\x17', 26) # RIGHT ADC INPUT GAIN, ADDRESS 0x01: unmute right ADC, input gain=0dB
# R2 and R3 are reserved
i2c.send(b'\x08\x08', 26) # ANALOG AUDIO PATH, ADDRESS 0x04: Bypass select, DAC not selected
i2c.send(b'\x0a\x08', 26) # DIGITAL AUDIO PATH, ADDRESS 0x05: leave default, DAC is muted
i2c.send(b'\x0c\x7e', 26) # POWER MANAGEMENT, ADDRESS 0x06: power on chip and line-in
#i2c.send(b'\x0e\x0a', 26) # DIGITAL AUDIO I/F, ADDRESS 0x07: I2S parameters, leave default
i2c.send(b'\x0e\x02', 26) # DIGITAL AUDIO I/F, ADDRESS 0x07: Set 16-bit, I2S mode
i2c.send(b'\x10\x00', 26) # SAMPLING RATE, ADDRESS 0x08: leave default

# Set up Codec for DAC playback:
i2c.send(b'\x08\x10', 26)
i2c.send(b'\x0a\x00', 26)
i2c.send(b'\x0c\x72', 26)
i2c.send(b'\x0e\x02', 26)
i2c.send(b'\x10\x00', 26)
i2c.send(b'\x12\x01', 26)

# tim = pyb.Timer
# def set_volume(tim, buf=bytearray(3)):
#     val = pot.read()
#     buf[0] = val
#     buf[1] = val >> 8
#     i2c.mem_write(buf, 0x32, 0, addr_size=16)
# tim.callback(set_volume)

tim = pyb.Timer(1, freq=20)
def set_volume(tim, buf=bytearray(1)):
    buf[0] = pot.read() >> 6
    i2c.mem_write(buf, 96, 2)
    

tim.callback(set_volume)

i2s = pyb.I2S()
i2s.init(i2s.MASTER, mclkout=1)
f = open('/sd/5_15-48kHz.wav', 'rb')
i2s.stream_out(f)

def test_stream():
    i2c.send(b'\x00\x17', 26) # LEFT IN GAIN = 0dB
    i2c.send(b'\x02\x17', 26) # RIGHT IN GAIN = 0dB
    i2c.send(b'\x08\x10', 26)

def test_mic():
    i2c.send(b'\x00\x27', 26) # LEFT IN GAIN = +24dB
    i2c.send(b'\x02\x27', 26) # RIGHT IN GAIN = +24dB
    i2c.send(b'\x08\x08', 26)



#
import codec
>>> codec.i2s.deinit()
>>> i2s = pyb.I2S()
>>> i2s.init(i2s.MASTER, mclkout=1)
>>> i2s.send_recv(b'0123456789abcdef')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OSError: 116
>>> i2s.init(i2s.MASTER, mclkout=1)
>>> i2s.send_recv(b'0123456789abcdef')
b'\xf5\xff\xfc\xff\xfc\xff\x02\x00\x06\x00\x12\x00\x08\x00\x02\x00'
>>> i2s.send_recv(b'0123456789abcdef')
b'\x0c\x00\r\x00\x11\x00\xfd\xff\r\x00\xf9\xff\x1b\x00\xe7\xff'
>>> i2s.send_recv(b'0123456789abcdef')
b"\x0c\x00\x08\x00#\x00\xf9\xff\xf3\xff'\x00#\x00\xf9\xff"
>>> i2s.send_recv(b'0123456789abcdef')
b'\xeb\xff1\x00F\x00\xbc\xff\xcc\xff[\x00\x88\x00\n\xff'
>>> i2s.send_recv(b'0123456789abcdef')
b'\xd5\xfe\x94\xfb\x1c\xfb\xfb\x00\x12\x01\t\xff\r\xffK\x01'
>>> i2s.send_recv(b'0123456789abcdef')
b')\x01.\x04\x11\x03o\xff\xac\xff\xd7\xff\xb3\xff[\x00'
>>> i2s.send_recv(b'0123456789abcdef')
b's\x00\xcd\x03l\x02\t\xff\xc0\xff\\\x00\x9e\xff\xe9\xfe'
>>> i2s.send_recv(b'0123456789abcdef')
b'\xba\x00H\xfc\n\x04^\x00f\xffn\xff\xc2\xff\x86\x00'
>>> i2s.send_recv(b'0123456789abcdef')
b'r\x00M\x03\xbe\x03/\xffR\xff@\x00\xd5\xff\xfb\xfe'
>>> i2s.send_recv(b'0123456789abcdef')
b']\x00<\xfcU\x03u\x00=\xff`\xff\xf0\xff\x9d\x00'
>>> i2s.send_recv(b'0123456789abcdef')
b'\x18\x00>\x032\x037\xff\x1e\xffI\x00\xac\x00\xf4\xfe'
>>> i2s.send_recv(b'0123456789abcdef')
b"\xab\xfe)\xfc\xd0\xfa}\x00\xdd\x00r\xff'\xff\x8f\x00"
>>> i2s.send_recv(b'0123456789abcdef')
b'?\x01?\x03\n\x05\xfb\xfe\xdc\xfez\x00\x9a\x00\x84\xfe'
>>> i2s.send_recv(b'0123456789abcdef')
b'\x9e\xfe\x9b\xfb*\xfb3\x00\xc0\x00\x03\x00J\xff\xfe\xfe'
>>> 



>>> import codec
>>> codec.i2s.deinit()
>>> i2s = pyb.I2S()
>>> i2s.init(i2s.MASTER, mclkout=1)
>>> b1 = bytearray(32)
>>> b2 = bytearray(32)
>>> i2s.send_recv(b1,b2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OSError: 116
>>> i2s.init(i2s.MASTER, mclkout=1)
>>> i2s.send_recv(b1,b2)
bytearray(b"\x1b\x00\n\x00\x0f\x00\x04\x00 \x00'\x00\x01\x00\x05\x00\x12\x007\x00\xe6\xff\xf5\xff\x1c\x00;\x00\xd3\xff\xc1\xff")
>>> struct.unpack('h',b2[4:6])[0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'struct' is not defined
>>> import struct
>>> struct.unpack('h',b2[4:6])[0]
15
>>> struct.unpack('h',b2[6:8])[0]
4


import os
os.listdir('/sd')
os.rmdir('/sd/test.wav')
import codec
codec.i2s.stop()
codec.i2c.send(b'\x00\x20', 26)
codec.i2c.send(b'\x02\x20', 26)
codec.i2c.send(b'\x0a\x06', 26)
f1 = open('/sd/test.wav', 'wb')
codec.i2s.stream_in(f1)
codec.i2s.stop()
f1.flush()
f1.close()
f1 = open('/sd/test.wav', 'rb')
codec.i2s.stream_out(f1)

codec.i2s.stop('stream_out')
codec.i2s.stop('stream_in')
codec.i2s.stop()
