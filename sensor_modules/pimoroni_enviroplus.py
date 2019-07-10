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
from time import sleep
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from operations_modules import logger
from operations_modules import file_locations

round_decimal_to = 5
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)


class CreateEnviroPlus:
    """ Creates Function access to the Pimoroni Enviro+. """
    def __init__(self):
        try:
            self.enviroplus_import = __import__('enviroplus', fromlist=['gas'])
            self.pms5003_import = __import__('pms5003')
            self.bme280_import = __import__('bme280')
            self.ST7735_import = __import__('ST7735')
            self.ltr559_import = __import__('ltr559')
        except Exception as error:
            logger.sensors_logger.warning("Pimoroni Enviro+ Module Load Failure - " + str(error))

        try:
            self.bme280 = self.bme280_import.BME280()
        except Exception as error:
            logger.sensors_logger.warning("Pimoroni Enviro+ BME280 Initialization Failure - " + str(error))

        try:
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
            self.top_pos = 25
            self.x = 0
            self.y = 0
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Initialization - Failed: " + str(error))

        try:
            self.font = ImageFont.truetype(file_locations.enviro_plus_font, 20)
            self.img = Image.new('RGB', (self.st7735.width, self.st7735.height), color=(0, 0, 0))
            self.draw = ImageDraw.Draw(self.img)
        except Exception as error:
            logger.sensors_logger.warning("Pimoroni Enviro+ PIL Initialization Failure - " + str(error))

        # First readings seem to return an error.  Getting them over with before needing readings
        self.bme280.get_temperature()
        sleep(0.5)
        self.bme280.get_humidity()
        sleep(0.5)
        self.bme280.get_pressure()
        sleep(0.5)
        self.ltr559_import.get_lux()

    def _update_message_display_x_y(self, message, line_number):
        # Calculate text position
        size_x, size_y = self.draw.textsize(message, self.font)

        self.x = (self.st7735.width - size_x) / 2
        self.y = (self.st7735.height / line_number) - (size_y / line_number)

    # Displays text on the 0.96" LCD
    def display_text(self, message):
        line_count = 0
        multi_line_message = []
        count = 0
        while count < len(message):
            multi_line_message.append(message[count:count + 12] + "\n")
            count += 12
            line_count += 1

        try:
            # Draw background rectangle and write text.
            self.draw.rectangle((0, 0, 160, 80), back_colour)
            # Write the text at the top in black
            self.draw.text((self.x, self.y), message, font=self.font, fill=text_colour)
            if line_count > 1:
                self._update_message_display_x_y(message, 2)
                self.draw.text((self.x, self.y), message, font=self.font, fill=text_colour)
            if line_count > 2:
                self._update_message_display_x_y(message, 3)
                self.draw.text((self.x, self.y), message, font=self.font, fill=text_colour)
            self.st7735.display(self.img)
            sleep(10)
            self.st7735.set_backlight(0)
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Display - Failed - " + str(error))

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
