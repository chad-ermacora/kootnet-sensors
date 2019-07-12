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
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import file_locations

round_decimal_to = 5
turn_off_display_seconds = 25


class CreateEnviroPlus:
    """ Creates Function access to the Pimoroni Enviro+. """
    def __init__(self):
        try:
            self.display_off_count = 0
            self.display_is_on = True
            self.display_ready = True
            self.font = ImageFont.truetype(file_locations.display_font, 40)

            self.enviroplus_import = __import__('enviroplus', fromlist=['gas'])
            self.pms5003_import = __import__('pms5003')
            self.bme280_import = __import__('bme280')
            self.ST7735_import = __import__('ST7735')
            self.ltr559_import = __import__('ltr559')

            self.bme280 = self.bme280_import.BME280()

            # Create ST7735 LCD display class
            self.st7735 = self.ST7735_import.ST7735(
                port=0,
                cs=1,
                dc=9,
                backlight=12,
                rotation=270,
                spi_speed_hz=10000000
            )
            # Initialize display
            self.st7735.begin()

            # First readings seem to return an error.  Getting them over with before needing readings
            self.bme280.get_temperature()
            time.sleep(0.5)
            self.bme280.get_humidity()
            time.sleep(0.5)
            self.bme280.get_pressure()
            time.sleep(0.5)
            self.ltr559_import.get_lux()

            self.thread_display_power_saving = Thread(target=self._display_timed_off)
            self.thread_display_power_saving.daemon = True
            self.thread_display_power_saving.start()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Initialization Failed - " + str(error))
            configuration_main.installed_sensors.pimoroni_enviroplus = 0
            configuration_main.installed_sensors.pimoroni_pms5003 = 0

    def _display_timed_off(self):
        while True:
            if self.display_is_on:
                if self.display_off_count > turn_off_display_seconds:
                    self.st7735.set_backlight(0)
                    self.display_is_on = False
                else:
                    self.display_off_count += 1
            time.sleep(1)

    # Displays text on the 0.96" LCD
    def display_text(self, message):
        if self.display_ready:
            self.display_ready = False
            message_img = Image.new('RGB', (self.st7735.width, self.st7735.height), color=(0, 0, 0))
            blank_img = Image.new('RGB', (self.st7735.width, self.st7735.height), color=(0, 0, 0))
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
                    time.sleep(.1)
                self.st7735.display(blank_img)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni Enviro+ Display - Failed - " + str(error))

            self.display_ready = True
        else:
            logger.sensors_logger.warning("Unable to display message on Pimoroni Enviro+.  Already in use.")

    def temperature(self):
        """ Returns Temperature as a Float. """
        try:
            temp_var = float(self.bme280.get_temperature())
            logger.sensors_logger.debug("Pimoroni Enviro+ Temperature - OK")
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Temperature - Failed - " + str(error))
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        try:
            pressure_hpa = self.bme280.get_pressure()
            logger.sensors_logger.debug("Pimoroni Enviro+ Pressure - OK")
        except Exception as error:
            pressure_hpa = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Pressure - Failed - " + str(error))
        return int(pressure_hpa)

    def humidity(self):
        """ Returns Humidity as a Float. """
        try:
            var_humidity = self.bme280.get_humidity()
            logger.sensors_logger.debug("Pimoroni Enviro+ Humidity - OK")
        except Exception as error:
            var_humidity = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Humidity - Failed - " + str(error))
        return round(var_humidity, round_decimal_to)

    def lumen(self):
        """ Returns Lumen as a Float. """
        try:
            lumen = float(self.ltr559_import.get_lux())
            logger.sensors_logger.debug("Pimoroni Enviro+ Lumen - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Lumen - Failed - " + str(error))
            lumen = 0.0
        return round(lumen, round_decimal_to)

    def distance(self):
        """ Returns distance in cm?. """
        try:
            distance = float(self.ltr559_import.get_proximity())
            logger.sensors_logger.debug("Pimoroni Enviro+ Proximity - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Proximity - Failed - " + str(error))
            distance = 0.0
        return round(distance, round_decimal_to)

    def gas_data(self):
        """ Returns 3 gas readings Oxidised, Reduced and nh3 as a list. """
        try:
            enviro_plus_gas_data = self.enviroplus_import.gas.read_all()
            oxidised = enviro_plus_gas_data.oxidising / 1000
            reduced = enviro_plus_gas_data.reducing / 1000
            nh3 = enviro_plus_gas_data.nh3 / 1000

            gas_list_oxidised_reduced_nh3 = [round(oxidised, round_decimal_to), round(reduced, round_decimal_to), round(nh3, round_decimal_to)]

            logger.sensors_logger.debug("Pimoroni Enviro+ GAS - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ GAS - Failed - " + str(error))
            gas_list_oxidised_reduced_nh3 = [0.0, 0.0, 0.0]
        return gas_list_oxidised_reduced_nh3

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings pm1, pm25 and pm10 as a list. """
        try:
            enviro_plus_pm_data = self.pms5003_import.read()
            pm1 = enviro_plus_pm_data.pm_ug_per_m3(1.0)
            pm25 = enviro_plus_pm_data.pm_ug_per_m3(2.5)
            pm10 = enviro_plus_pm_data.pm_ug_per_m3(10)

            pm_list_pm1_pm25_pm10 = [round(pm1, round_decimal_to), round(pm25, round_decimal_to), round(pm10, round_decimal_to)]

            logger.sensors_logger.debug("Pimoroni Enviro+ Particulate Matter - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Particulate Matter - Failed - " + str(error))
            pm_list_pm1_pm25_pm10 = [0.0, 0.0, 0.0]
        return pm_list_pm1_pm25_pm10
