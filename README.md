# uPy_AudioCodec

The uPy_AudioCodec is a daughterboard for the MicroPython pyboard
containing an I2S Audio codec chip (the SSM2604 from Analog Devices)
and a headphone amplifier (the TPA6130A2 from Texas Instruments).

This repository contains the design files for the board along with
code to use it with MicroPython.

# Quick Start

To use the uPy_AudioCodec you will need the following:
* A MicroPython pyboard
* The codec board along with the optional microphone plug
* A 16-bit stereo *.wav file encoded at either 44.1kHz (CD-quality) or 48kHz
  sample rate. (Other sample rates are theoretically supported but
  untested so far.)

* A micro-SD card (to store the *.wav file)
* A pair of headphones or earbuds with 3.5mm (1/8") stereo plug

Assemble the daughterboard in the pyboard with the microphone plug and
headphone plugged in as shown in the picture. Note that the
daughterboard must occupy the 'Y' position in the pyboard, as the SPI
port in the 'X' position (SPI1) does not support I2S.

![codec daughterboard in pyboard](/images/codec_board.jpg)


Use DFU to load I2S supporting uPy firmware to pyboard:
firmware/i2s-firmware.dfu

(I will do my best to keep this firmware image up to date with the
`i2s` branch of github.com/blmorris/micropython)

The following code is a very quick-and-dirty way to initialize the
AudioCodec board in python - I will clean this up soon!:

```Python
import pyb
pot = pyb.ADC('Y12')
hpctl = pyb.Pin('Y11')
hpctl.init(hpctl.OUT_PP)
hpctl.high()
i2c = pyb.I2C(2)
i2c.init(i2c.MASTER)
# Might do a 'try' here to make sure both i2c devices are working:
i2c.scan()
# Should give [26, 96]

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

tim = pyb.Timer(1, freq=20)
def set_volume(tim, buf=bytearray(1)):
    buf[0] = pot.read() >> 6
    i2c.mem_write(buf, 96, 2)
    

tim.callback(set_volume)

i2s = pyb.I2S()
i2s.init(i2s.MASTER, mclkout=1)
i2s.stream_out(f)

def test_stream():
    i2c.send(b'\x00\x17', 26) # LEFT IN GAIN = 0dB
    i2c.send(b'\x02\x17', 26) # RIGHT IN GAIN = 0dB
    i2c.send(b'\x08\x10', 26)

def test_mic():
    i2c.send(b'\x00\x27', 26) # LEFT IN GAIN = +24dB
    i2c.send(b'\x02\x27', 26) # RIGHT IN GAIN = +24dB
    i2c.send(b'\x08\x08', 26)

```

Then the following to start streaming out to your headphones:

```Python
f = open('/path/to/wave/file', 'rb')
f.seek(44) # to skip past wave file header
i2s.stream_out(f)
```
