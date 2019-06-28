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
from operations_modules import logger

round_decimal_to = 5


class CreateEnviroPlus:
    """ Creates Function access to the Pimoroni Enviro+. """
    def __init__(self):
        self.enviroplus_import = __import__('enviroplus', fromlist=['gas'])
        self.bme280_import = __import__('bme280')
        self.ST7735_import = __import__('ST7735')
        self.ltr559_import = __import__('ltr559')
        self.time = __import__('time')
        self.colorsys = __import__('colorsys')
        self.os = __import__('os')
        self.sys = __import__('sys')
        self.PIL_import = __import__('os')

        try:
            self.pms5003_import = __import__('pms5003')
            logger.sensors_logger.debug("Pimoroni Enviro+ Particulate Matter Sensor - OK")
        except Exception as error:
            logger.sensors_logger.warning("Pimoroni Enviro+ Particulate Matter Sensor - Not Installed " + str(error))

        try:
            self.bme280 = self.bme280_import.BME280()
            try:
                self.pms5003 = self.pms5003_import.PMS5003()
                logger.sensors_logger.debug("Pimoroni Enviro+ Particulate Matter Sensor - OK")
            except Exception as error:
                logger.sensors_logger.debug("Pimoroni Enviro+ Particulate Matter Sensor - Not Installed " + str(error))

            self.Image = self.PIL_import.Image()
            self.ImageDraw = self.PIL_import.ImageDraw()
            self.ImageFont = self.PIL_import.ImageFont()

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

            self.WIDTH = self.st7735.width
            self.HEIGHT = self.st7735.height

            # Set up canvas and font
            self.img = self.Image.new('RGB', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
            self.draw = self.ImageDraw.Draw(self.img)
            self.path = self.os.path.dirname(self.os.path.realpath(__file__))
            self.font = self.ImageFont.truetype(self.path + "/fonts/Asap/Asap-Bold.ttf", 20)

            self.message = ""

            # The position of the top bar
            self.top_pos = 25

        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Initialization - Failed: " + str(error))

    # Displays data and text on the 0.96" LCD
    def display_text(self, variable, data, unit):
        # Maintain length of list
        self.values[variable] = self.values[variable][1:] + [data]
        # Scale the values for the variable between 0 and 1
        colours = [(v - min(self.values[variable]) + 1) / (max(self.values[variable])
                   - min(self.values[variable]) + 1) for v in self.values[variable]]
        # Format the variable name and value
        self.message = "{}: {:.1f} {}".format(variable[:4], data, unit)
        print(self.message)
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), (255, 255, 255))
        for i in range(len(colours)):
            # Convert the values to colours from red to blue
            colour = (1.0 - colours[i]) * 0.6
            r, g, b = [int(x * 255.0) for x in self.colorsys.hsv_to_rgb(colour,
                       1.0, 1.0)]
            # Draw a 1-pixel wide rectangle of colour
            self.draw.rectangle((i, self.top_pos, i+1, self.HEIGHT), (r, g, b))
            # Draw a line graph in black
            line_y = self.HEIGHT - (self.top_pos + (colours[i] * (self.HEIGHT - self.top_pos)))\
                     + self.top_pos
            self.draw.rectangle((i, line_y, i+1, line_y+1), (0, 0, 0))
        # Write the text at the top in black
        self.draw.text((0, 0), self.message, font=self.font, fill=(0, 0, 0))
        self.ST7735_import.display(self.img)

    def temperature(self):
        """ Returns Temperature as a Float. """
        try:
            temp_var = float(self.bme280.get_temperature())
            logger.sensors_logger.debug("Pimoroni Enviro+ Temperature - OK")
        except Exception as error:
            temp_var = 0
            logger.sensors_logger.error("Pimoroni Enviro+ Temperature - Failed - " + str(error))
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        try:
            pressure_hpa = self.bme280.get_pressure()
            logger.sensors_logger.debug("Pimoroni Enviro+ Pressure - OK")
        except Exception as error:
            pressure_hpa = 0
            logger.sensors_logger.error("Pimoroni Enviro+ Pressure - Failed - " + str(error))

        return int(pressure_hpa)

    def humidity(self):
        """ Returns Humidity as a Float. """
        try:
            var_humidity = self.bme280.get_humidity()
            logger.sensors_logger.debug("Pimoroni Enviro+ Humidity - OK")
        except Exception as error:
            var_humidity = 0
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
            enviro_plus_pm_data = self.pms5003.read()
            pm1 = enviro_plus_pm_data.pm_ug_per_m3(1.0)
            pm25 = enviro_plus_pm_data.pm_ug_per_m3(2.5)
            pm10 = enviro_plus_pm_data.pm_ug_per_m3(10)

            pm_list_pm1_pm25_pm10 = [round(pm1, round_decimal_to), round(pm25, round_decimal_to), round(pm10, round_decimal_to)]

            logger.sensors_logger.debug("Pimoroni Enviro+ Particulate Matter - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Particulate Matter - Failed - " + str(error))
            pm_list_pm1_pm25_pm10 = [0.0, 0.0, 0.0]

        return pm_list_pm1_pm25_pm10
