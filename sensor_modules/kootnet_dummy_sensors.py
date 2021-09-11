"""
This module is a 'dummy' sensor for testing
It Returns randomly generated data that resembles real sensor data of it's type

Created on Mon May 4 09:34:56 2020

@author: OO-Dragon
"""
import time
import datetime
import random
from operations_modules import logger

round_decimal_to = 5
pause_sensor_during_access_sec = 0.005

senor_delay_min = 0.001
sensor_delay_max = 0.015


class CreateDummySensors:
    """ Creates Function access to the Kootnet Dummy Sensors. """

    def __init__(self):
        self.sensor_in_use = False
        self.display_in_use = False
        logger.sensors_logger.debug("Kootnet Dummy Sensors Initialization - OK")

    def display_text(self, message):
        """ Records provided text to the Sensor log. """
        if not self.display_in_use:
            self.display_in_use = True
            time.sleep(10)
            logger.sensors_logger.info("Kootnet Dummy Display: " + message)
            self.display_in_use = False
        else:
            logger.sensors_logger.debug("Kootnet Dummy Display - In Use")

    def cpu_temperature(self):
        """ Returns System CPU Temperature as a Float in Celsius. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=25, max_number=85)

    def temperature(self):
        """ Returns Temperature as a Float in Celsius. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=-20, max_number=65)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_int(min_number=650, max_number=1200)

    def humidity(self):
        """ Returns Altitude as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=35, max_number=65)

    def distance(self):
        """ Returns Altitude as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=25, max_number=133)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=25, max_number=133)

    def gas_data(self):
        """ Returns 3 gas readings Oxidised, Reduced and nh3 as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_tri_float(min_number=200, max_number=2200)

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings pm1, pm25 and pm10 as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return [self._get_random_float(min_number=10, max_number=135),
                self._get_random_float(min_number=10, max_number=135),
                self._get_random_float(min_number=10, max_number=135),
                self._get_random_float(min_number=10, max_number=135)]

    def ultra_violet_index(self):
        """ Returns Ultra Violet (A,B) comparators as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        uv_index = self._get_random_float(min_number=0, max_number=65)
        self.sensor_in_use = False
        return uv_index

    def ultra_violet(self):
        """ Returns Ultra Violet (A,B) as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        ultra_a = self._get_random_float(min_number=0, max_number=65)
        ultra_b = self._get_random_float(min_number=0, max_number=65)
        return [ultra_a, ultra_b]

    def lumen(self):
        """ Returns Lumen as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_float(min_number=5, max_number=1700)

    def spectral_six_channel(self):
        """ Returns Red, Orange, Yellow, Green, Blue and Violet as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return_six = self._get_random_tri_float(min_number=10, max_number=135) + \
                     self._get_random_tri_float(min_number=10, max_number=135)
        return return_six

    def accelerometer_xyz(self):
        """ Returns Accelerometer X, Y, Z as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_tri_float(min_number=0, max_number=0)

    def magnetometer_xyz(self):
        """ Returns Magnetometer X, Y, Z as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_tri_float(min_number=35, max_number=85)

    def gyroscope_xyz(self):
        """ Returns Gyroscope X, Y, Z as floats in a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False
        return self._get_random_tri_float(min_number=0, max_number=135)

    def get_all_gps_data(self):
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        time.sleep(random.uniform(senor_delay_min, sensor_delay_max))
        self.sensor_in_use = False

        timestamp = datetime.datetime.utcnow().strftime("%H:%M:%S")
        latitude = self._get_random_float(min_number=-89, max_number=89)
        longitude = self._get_random_float(min_number=-179, max_number=179)
        altitude = self._get_random_float(min_number=0, max_number=2100)
        number_of_connected_satellites = self._get_random_int(min_number=0, max_number=32)
        gps_quality = self._get_random_int()

        pdop = self._get_random_float(min_number=0, max_number=50)
        hdop = self._get_random_float(min_number=0, max_number=50)
        vdop = self._get_random_float(min_number=0, max_number=50)

        speed_over_ground = self._get_random_float(min_number=0, max_number=22)
        mode_fix_type = self._get_random_int(min_number=1, max_number=3)

        return [latitude, longitude, altitude, timestamp, number_of_connected_satellites,
                gps_quality, mode_fix_type, speed_over_ground, pdop, hdop, vdop]

    @staticmethod
    def _get_random_float(min_number=1, max_number=100):
        whole_numbers = random.randint(min_number, max_number)
        decimal_numbers = random.random()
        return round(float(whole_numbers) + decimal_numbers, round_decimal_to)

    @staticmethod
    def _get_random_tri_float(min_number=1, max_number=100):
        tri_return = []
        for i in range(3):
            whole_numbers = random.randint(min_number, max_number)
            decimal_numbers = random.random()
            tri_return.append(round(whole_numbers + decimal_numbers, round_decimal_to))
        return tri_return

    @staticmethod
    def _get_random_int(min_number=1, max_number=100):
        return random.randint(min_number, max_number)
