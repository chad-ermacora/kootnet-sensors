"""
This module is for the Pimoroni Enviro+
It Retrieves & Returns Sensor data to be written to the DB

BME280 temperature, pressure, humidity sensor
LTR-559 light and proximity sensor
MICS6814 analog gas sensor
ADS1015 analog to digital converter (ADC)
MEMS microphone
0.96" colour LCD (160x80)
Connector for particulate matter (PM) sensor*

pip install enviroplus

Created on Tue June 25 10:53:56 2019

@author: OO-Dragon
"""
import time
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access
from operations_modules import file_locations
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

round_decimal_to = 5
turn_off_display_seconds = 25
pause_sensor_during_access_sec = 0.02
pause_sensor_during_access_sec_gas = 0.095


class CreateEnviroPlus:
    """ Creates Function access to the Pimoroni Enviro+. """

    def __init__(self):
        try:
            self.display_off_count = 0
            self.display_is_on = True

            self.display_in_use = False
            self.sensor_in_use = False

            self.font = ImageFont.truetype(file_locations.display_font, 40)

            ltr559_import = __import__("sensor_modules.drivers.ltr559", fromlist=["LTR559"])
            bme280_import = __import__("sensor_modules.drivers.enviroplus.custom-bme280", fromlist="BME280")
            self.gas_access = __import__("sensor_modules.drivers.enviroplus.mics6814", fromlist=["read_all"])
            self.ltr_559 = ltr559_import.LTR559()
            self.bme280 = bme280_import.BME280()
            # Setup & Initialize display
            st7735_import = __import__("sensor_modules.drivers.ST7735", fromlist=["ST7735"])
            self.st7735 = st7735_import.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
            self.st7735.begin()

            # Start thread to turn off display after set amount of seconds (Set after top file imports)
            self.thread_display_power_saving = Thread(target=self._display_timed_off)
            self.thread_display_power_saving.daemon = True
            self.thread_display_power_saving.start()
            logger.sensors_logger.debug("Pimoroni Enviro+ Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_enviroplus = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _display_timed_off(self):
        while True:
            if self.display_is_on:
                if self.display_off_count > turn_off_display_seconds:
                    self.st7735.set_backlight(0)
                    self.display_is_on = False
                else:
                    self.display_off_count += 1
            time.sleep(1)

    def display_text(self, message):
        """ Scrolls Provided Text on LED Display. """
        if not self.display_in_use:
            self.display_in_use = True
            message_img = Image.new('RGB', (self.st7735.width, self.st7735.height), color=(0, 0, 0))
            blank_img = message_img
            draw = ImageDraw.Draw(message_img)

            self.st7735.set_backlight(1)
            self.display_off_count = 0
            self.display_is_on = True

            size_x, size_y = draw.textsize(message, self.font)
            text_x = 160
            text_y = (80 - size_y) // 2

            t_start = time.time()
            try:
                while self.display_off_count < turn_off_display_seconds and self.display_is_on:
                    x = (time.time() - t_start) * 80
                    x %= (size_x + 160)
                    draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                    draw.text((int(text_x - x), text_y), message, font=self.font, fill=(255, 255, 255))
                    self.st7735.display(message_img)
                    time.sleep(0.1)
                self.st7735.display(blank_img)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni Enviro+ Display - Failed: " + str(error))
            self.display_in_use = False
        else:
            logger.sensors_logger.debug("Unable to display message on Pimoroni Enviro+.  Already in use.")

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = float(self.bme280.get_temperature())
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            pressure_hpa = self.bme280.get_pressure()
        except Exception as error:
            pressure_hpa = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Pressure - Failed: " + str(error))
        self.sensor_in_use = False
        return int(pressure_hpa)

    def humidity(self):
        """ Returns Humidity as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            var_humidity = self.bme280.get_humidity()
        except Exception as error:
            var_humidity = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Humidity - Failed: " + str(error))
        self.sensor_in_use = False
        return round(var_humidity, round_decimal_to)

    def lumen(self):
        """ Returns Lumen as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            lumen = float(self.ltr_559.get_lux())
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Lumen - Failed: " + str(error))
            lumen = 0.0
        self.sensor_in_use = False
        return round(lumen, round_decimal_to)

    def distance(self):
        """ Returns distance in cm?. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            distance = float(self.ltr_559.get_proximity())
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Proximity - Failed: " + str(error))
            distance = 0.0
        self.sensor_in_use = False
        return round(distance, round_decimal_to)

    def gas_data(self):
        """ Returns 3 gas readings Oxidised, Reduced and nh3 as a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec_gas)
        self.sensor_in_use = True
        try:
            enviro_plus_gas_data = self.gas_access.read_all()
            oxidised = enviro_plus_gas_data.oxidising / 1000
            reduced = enviro_plus_gas_data.reducing / 1000
            nh3 = enviro_plus_gas_data.nh3 / 1000

            gas_list_oxidised_reduced_nh3 = [round(oxidised, round_decimal_to),
                                             round(reduced, round_decimal_to),
                                             round(nh3, round_decimal_to)]

        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ GAS - Failed: " + str(error))
            gas_list_oxidised_reduced_nh3 = [0.0, 0.0, 0.0]
        self.sensor_in_use = False
        return gas_list_oxidised_reduced_nh3
