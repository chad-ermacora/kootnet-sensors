import time
import threading
import math
import RPi.GPIO as GPIO
from sensor_modules.drivers.ioexpander import ioexpander as io
from sensor_modules.drivers.bme280 import BME280
from sensor_modules.drivers.ltr559 import LTR559
from sensor_modules.drivers.smbus2 import SMBus
from .history import wind_degrees_to_cardinal


__version__ = '0.0.1'


# Wind Vane
PIN_WV = 8     # P0.3 ANE6

# Anemometer
PIN_ANE1 = 5       # P0.0
PIN_ANE2 = 6       # P0.1

ANE_RADIUS = 7  # Radius from center to the center of a cup, in CM
ANE_CIRCUMFERENCE = ANE_RADIUS * 2 * math.pi
ANE_FACTOR = 2.18  # Anemometer factor

# Rain gauge
PIN_R2 = 3         # P1.2
PIN_R3 = 7         # P1.1
PIN_R4 = 2         # P1.0
PIN_R5 = 1         # P1.5
RAIN_MM_PER_TICK = 0.2794

wind_direction_to_degrees = {
    0.9: 0,
    2.0: 45,
    3.0: 90,
    2.8: 135,
    2.5: 180,
    1.5: 225,
    0.3: 270,
    0.6: 315
}


class WeatherHAT:
    def __init__(self):
        self.updated_wind_rain = False
        self._lock = threading.Lock()
        self._i2c_dev = SMBus(1)

        self._bme280 = BME280(i2c_dev=self._i2c_dev)
        self._ltr559 = LTR559(i2c_dev=self._i2c_dev)

        self._ioe = io.IOE(i2c_addr=0x12, interrupt_pin=4)

        # Fudge to enable pull-up on interrupt pin
        self._ioe._gpio.setup(self._ioe._interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Input voltage of IO Expander, this is 3.3 on Breakout Garden
        self._ioe.set_adc_vref(3.3)

        # Wind Vane
        self._ioe.set_mode(PIN_WV, io.ADC)

        # Anemometer
        self._ioe.set_mode(PIN_ANE1, io.OUT)
        self._ioe.output(PIN_ANE1, 0)
        self._ioe.set_pin_interrupt(PIN_ANE2, True)
        self._ioe.setup_switch_counter(PIN_ANE2)

        # Rain Sensor
        self._ioe.set_mode(PIN_R2, io.IN_PU)
        self._ioe.set_mode(PIN_R3, io.OUT)
        self._ioe.set_mode(PIN_R4, io.IN_PU)
        self._ioe.setup_switch_counter(PIN_R4)
        self._ioe.set_mode(PIN_R5, io.IN_PU)
        self._ioe.output(PIN_R3, 0)
        self._ioe.set_pin_interrupt(PIN_R4, True)
        self._ioe.on_interrupt(self.handle_ioe_interrupt)
        self._ioe.clear_interrupt()

        # Data API... kinda
        self.temperature_offset = 0
        self.device_temperature = 0
        self.temperature = 0

        self.pressure = 0

        self.humidity = 0
        self.relative_humidity = 0
        self.dewpoint = 0

        self.lux = 0

        self.wind_speed = 0
        self.wind_direction = 0

        self.rain = 0
        self.rain_total = 0

        self.reset_counts()

    def reset_counts(self):
        self._lock.acquire(blocking=True)
        self._ioe.clear_switch_counter(PIN_ANE2)
        self._ioe.clear_switch_counter(PIN_R4)
        self._lock.release()

        self._wind_counts = 0
        self._rain_counts = 0
        self._last_wind_counts = 0
        self._last_rain_counts = 0
        self._t_start = time.time()

    def compensate_humidity(self, humidity, temperature, corrected_temperature):
        """Compensate humidity.

        Convert humidity to relative humidity.

        """
        dewpoint = self.get_dewpoint(humidity, temperature)
        corrected_humidity = 100 - (5 * (corrected_temperature - dewpoint)) - 20
        return min(100, max(0, corrected_humidity))

    def get_dewpoint(self, humidity, temperature):
        """Calculate Dewpoint."""
        return temperature - ((100 - humidity) / 5)

    def hpa_to_inches(self, hpa):
        """Convert hextopascals to inches of mercury."""
        return hpa * 0.02953

    def degrees_to_cardinal(self, degrees):
        value, cardinal = min(wind_degrees_to_cardinal.items(), key=lambda item: abs(item[0] - degrees))
        return cardinal

    def update(self, interval=60.0):
        # Time elapsed since last update
        delta = time.time() - self._t_start

        self.updated_wind_rain = False

        # Always update TPHL & Wind Direction
        self._lock.acquire(blocking=True)

        self.device_temperature = self._bme280.get_temperature()
        self.temperature = self.device_temperature + self.temperature_offset

        self.pressure = self._bme280.get_pressure()
        self.humidity = self._bme280.get_humidity()

        self.relative_humidity = self.compensate_humidity(self.humidity, self.device_temperature, self.temperature)

        self.dewpoint = self.get_dewpoint(self.humidity, self.device_temperature)

        self.lux = self._ltr559.get_lux()

        self.wind_direction_raw = self._ioe.input(PIN_WV)

        self._lock.release()

        value, self.wind_direction = min(wind_direction_to_degrees.items(), key=lambda item: abs(item[0] - self.wind_direction_raw))

        # Don't update rain/wind data until we've sampled for long enough
        if delta < interval:
            return

        self.updated_wind_rain = True

        rain_hz = self._rain_counts / delta
        wind_hz = self._wind_counts / delta
        self.rain_total = self._rain_counts * RAIN_MM_PER_TICK
        self.reset_counts()

        # wind speed of 2.4km/h causes the switch to close once per second

        wind_hz /= 2.0  # Two pulses per rotation
        wind_cms = wind_hz * ANE_CIRCUMFERENCE * ANE_FACTOR
        self.wind_speed = wind_cms / 100.0

        self.rain = rain_hz * RAIN_MM_PER_TICK

    def handle_ioe_interrupt(self, pin):
        self._lock.acquire(blocking=True)
        self._ioe.clear_interrupt()

        wind_counts, _ = self._ioe.read_switch_counter(PIN_ANE2)
        rain_counts, _ = self._ioe.read_switch_counter(PIN_R4)

        # If the counter value is *less* than the previous value
        # then we know the 7-bit switch counter overflowed
        # We bump the count value by the lost counts between last_wind and 128
        # since at 127 counts, one more count will overflow us back to 0
        if wind_counts < self._last_wind_counts:
            self._wind_counts += 128 - self._last_wind_counts
            self._wind_counts += wind_counts
        else:
            self._wind_counts += wind_counts - self._last_wind_counts

        self._last_wind_counts = wind_counts

        if rain_counts < self._last_rain_counts:
            self._rain_counts += 128 - self._last_rain_counts
            self._rain_counts += rain_counts
        else:
            self._rain_counts += rain_counts - self._last_rain_counts

        self._last_rain_counts = rain_counts

        # print(wind_counts, rain_counts, self._wind_counts, self._rain_counts)

        self._lock.release()
