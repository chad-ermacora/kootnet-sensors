from sensor_modules.drivers.smbus2 import smbus2 as smbus
import RPi.GPIO as GPIO
# from ..ads1015 import ADS1015
from ..bmp280 import BMP280
from ..lsm303d import LSM303D
from ..tcs3472 import TCS3472

__version__ = '1.0.1'


class LEDS:
    def __init__(self, status=0):
        self.status = status

    def on(self):
        """Turn LEDs on."""
        self.status = 1
        GPIO.output(4, 1)
        return True

    def off(self):
        """Turn LEDs off."""
        self.status = 0
        GPIO.output(4, 0)

    def is_on(self):
        """Return True if LED is on."""
        if self.status == 1:
            return True
        else:
            return False

    def is_off(self):
        """Return True if LED is off."""
        if self.status == 0:
            return True
        else:
            return False


bus = None
if GPIO.RPI_REVISION == 2 or GPIO.RPI_REVISION == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, 0)

leds = LEDS()  # Only initialized to turn off LEDs
light = TCS3472(i2c_bus=bus)
weather = BMP280(i2c_addr=0x77, i2c_dev=bus)
motion = LSM303D(i2c_dev=bus)
# analog = ADS1015(i2c_dev=bus)
