import serial
from time import sleep

ser = serial.Serial("/dev/ttyACM0")
ser.write(chr(0xAA))
ser.flush()

print ser.portstr

def putc(c):
    ser.write(chr(c))
putc(0xaa)
putc(0x0c)
putc(0x04)
putc(0x00)
putc(0x70)
putc(0x2e)
ser.flush()

sleep(10)

cmd = 0x99
servo = 0x00
val = 0x4f
val2 = 0x4f

while 1:
    val += 0x05
    if val==0xff:
        val = 0x00
    print val
    sleep(0.2)
    ser.write(chr(cmd) + chr(servo) + chr(val))

