"""
This module is for the Pimoroni Weather HAT + Weather Sensors Kit
It Retrieves & Returns Sensor data to be written to the DB

1.54" IPS LCD screen (240 x 240)
Four user-controllable switches
BME280 temperature, pressure, humidity sensor (datasheet)
LTR-559 light and proximity sensor (datasheet)
Nuvoton MS51 microcontroller with inbuilt 12-bit ADC (datasheet)
RJ11 connectors for connecting wind and rain sensors
HAT-format board
Fully-assembled
Compatible with all 40-pin header Raspberry Pi models

Created on Tue March 23 19:10:00 2022

@author: OO-Dragon
"""
import time
import math
import threading
from operations_modules import logger
from configuration_modules import app_config_access
from sensor_modules.pimoroni.pimoroni_bme280 import CreateBME280
from sensor_modules.pimoroni.pimoroni_ltr_559 import CreateLTR559
from sensor_modules.drivers.ioexpander import ioexpander as io

round_decimal_to = 5
pause_sensor_during_access_sec = 0.02

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


class _WeatherHAT:
    def __init__(self):
        rpi_gpio = __import__("RPi.GPIO")
        GPIO = rpi_gpio.GPIO

        self.updated_wind_rain = False
        self._lock = threading.Lock()

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

    def update(self, interval=60.0):
        # Time elapsed since last update
        delta = time.time() - self._t_start

        self.updated_wind_rain = False

        # Always update TPHL & Wind Direction
        self._lock.acquire(blocking=True)
        self.wind_direction_raw = self._ioe.input(PIN_WV)
        self._lock.release()

        value, self.wind_direction = min(wind_direction_to_degrees.items(),
                                         key=lambda item: abs(item[0] - self.wind_direction_raw))

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


# ToDo: Create sensor access functions + db columns + add to other parts of program for new sensor types
class CreateWeatherHAT:
    """ Creates Function access to the Pimoroni Weather HAT. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            self.bme280 = CreateBME280()
            self.ltr559 = CreateLTR559()
            self.rain_wind = _WeatherHAT()
            self.bme280.temperature()
            self.ltr559.lumen()
            logger.sensors_logger.debug("Pimoroni Weather HAT Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Weather HAT Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_weather_hat = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def temperature(self):
        """ Returns Temperature as a Float. """
        return self.bme280.temperature()

    def pressure(self):
        """ Returns Pressure as an Integer. """
        return self.bme280.pressure()

    def humidity(self):
        """ Returns Humidity as a Float. """
        return self.bme280.humidity()

    def lumen(self):
        """ Returns Lumen as a Float. """
        return self.ltr559.lumen()

    def distance(self):
        """ Returns distance in cm?. """
        return self.ltr559.distance()

    def wind_speed(self):
        """ Returns Wind speeds in km/h. """
        self.rain_wind.update()
        return self.rain_wind.wind_speed

    def wind_direction(self):
        """ Returns Wind direction in text (North, East, etc.) """
        self.rain_wind.update()
        return self.rain_wind.wind_direction

    def rain(self):
        """ Returns rain amount in mm/s """
        self.rain_wind.update()
        return self.rain_wind.rain

    def rain_total(self):
        """ Returns rain amount in mm/s """
        self.rain_wind.update()
        return self.rain_wind.rain_total
