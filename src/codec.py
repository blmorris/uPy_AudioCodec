from pyb import ADC, I2S, Timer, I2C, Pin

pot = ADC('Y12')
hpctl = Pin('Y11')
hpctl.init(hpctl.OUT_PP)
hpctl.high()
i2c = I2C(2, I2C.MASTER)
# i2c.init(i2c.MASTER)
# Might do a 'try' here to make sure both i2c devices are working:
l = i2c.scan()
for i in l:
    print(i)

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
i2c.send(b'\x0e\x0a', 26) # DIGITAL AUDIO I/F, ADDRESS 0x07: I2S parameters, leave default
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

tim = Timer(1, freq=20)
def set_volume(tim, buf=bytearray(1)):
    buf[0] = pot.read() >> 6
    i2c.mem_write(buf, 96, 2)
    

tim.callback(set_volume)

i2s = I2S()
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


def cbk(self):
    print('Callback!')

i2s.callback(cbk)





