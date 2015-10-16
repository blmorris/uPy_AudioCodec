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
