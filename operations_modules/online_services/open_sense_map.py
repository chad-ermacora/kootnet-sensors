"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import requests
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import app_cached_variables
from operations_modules.app_validation_checks import valid_sensor_reading

# Weather Underground URL Variables
open_sense_map_main_url_start = "https://api.opensensemap.org/boxes"
open_sense_map_login_url = "https://api.opensensemap.org/users/sign-in"


class CreateOpenSenseMapConfig:
    """ Creates a Open Sense Map Configuration object. """

    def __init__(self):
        self.sensor_access = None

        self.open_sense_map_enabled = 0
        self.sense_box_id = ""
        self.interval_seconds = 900.0

        self.temperature_id = ""
        self.pressure_id = ""
        self.altitude_id = ""
        self.humidity_id = ""
        self.gas_voc_id = ""
        self.gas_oxidised_id = ""
        self.gas_reduced_id = ""
        self.gas_nh3_id = ""
        self.pm1_id = ""
        self.pm2_5_id = ""
        self.pm10_id = ""

        self.lumen_id = ""
        self.red_id = ""
        self.orange_id = ""
        self.yellow_id = ""
        self.green_id = ""
        self.blue_id = ""
        self.violet_id = ""

        self.ultra_violet_index_id = ""
        self.ultra_violet_a_id = ""
        self.ultra_violet_b_id = ""

        self.bad_load = False

    def get_configuration_str(self):
        """ Returns Open Sense Map settings ready to be written to the configuration file. """
        config_str = "Enable = 1 & Disable = 0\n" + \
                     str(self.open_sense_map_enabled) + " = Enable Open Sense Map\n" + \
                     str(self.sense_box_id) + " = SenseBox ID\n" + \
                     str(self.interval_seconds) + " = Send to Server in Seconds\n" + \
                     str(self.temperature_id) + " = Temperature Sensor ID\n" + \
                     str(self.pressure_id) + " = Pressure Sensor ID\n" + \
                     str(self.altitude_id) + " = Altitude Sensor ID\n" + \
                     str(self.humidity_id) + " = Humidity Sensor ID\n" + \
                     str(self.gas_voc_id) + " = Gas VOC Sensor ID\n" + \
                     str(self.gas_nh3_id) + " = Gas NH3 Sensor ID\n" + \
                     str(self.gas_oxidised_id) + " = Gas Oxidised Sensor ID\n" + \
                     str(self.gas_reduced_id) + " = Gas Reduced Sensor ID\n" + \
                     str(self.pm1_id) + " = PM 1.0 Sensor ID\n" + \
                     str(self.pm2_5_id) + " = PM 2.5 Sensor ID\n" + \
                     str(self.pm10_id) + " = PM 10 Sensor ID\n" + \
                     str(self.lumen_id) + " = Lumen Sensor ID\n" + \
                     str(self.red_id) + " = Red Sensor ID\n" + \
                     str(self.orange_id) + " = Orange Sensor ID\n" + \
                     str(self.yellow_id) + " = Yellow Sensor ID\n" + \
                     str(self.green_id) + " = Green Sensor ID\n" + \
                     str(self.blue_id) + " = Blue Sensor ID\n" + \
                     str(self.violet_id) + " = Violet Sensor ID\n" + \
                     str(self.ultra_violet_index_id) + " = Ultra Violet Index Sensor ID\n" + \
                     str(self.ultra_violet_a_id) + " = Ultra Violet A Sensor ID\n" + \
                     str(self.ultra_violet_b_id) + " = Ultra Violet B Sensor ID"

        return config_str

    def update_open_sense_map_html(self, html_request):
        """ Updates & Writes Open Sense Map settings based on provided HTML request. """
        if html_request.form.get("enable_open_sense_map") is not None:
            self.open_sense_map_enabled = 1
        else:
            self.open_sense_map_enabled = 0

        if html_request.form.get("osm_station_id") is not None:
            self.sense_box_id = html_request.form.get("osm_station_id").strip()
        else:
            self.sense_box_id = ""

        if html_request.form.get("osm_interval") is not None:
            try:
                self.interval_seconds = float(html_request.form.get("osm_interval").strip())
            except Exception as error:
                logger.primary_logger.warning("Open Sense Map Invalid Interval: " + str(error))
                self.interval_seconds = 900.0
        else:
            self.interval_seconds = 900.0

        if html_request.form.get("env_temp_id") is not None:
            self.temperature_id = html_request.form.get("env_temp_id").strip()
        else:
            self.temperature_id = ""
        if html_request.form.get("pressure_id") is not None:
            self.pressure_id = html_request.form.get("pressure_id").strip()
        else:
            self.pressure_id = ""
        if html_request.form.get("altitude_id") is not None:
            self.altitude_id = html_request.form.get("altitude_id").strip()
        else:
            self.altitude_id = ""
        if html_request.form.get("humidity_id") is not None:
            self.humidity_id = html_request.form.get("humidity_id").strip()
        else:
            self.humidity_id = ""
        if html_request.form.get("gas_index_id") is not None:
            self.gas_voc_id = html_request.form.get("gas_index_id").strip()
        else:
            self.gas_voc_id = ""
        if html_request.form.get("gas_nh3_id") is not None:
            self.gas_nh3_id = html_request.form.get("gas_nh3_id").strip()
        else:
            self.gas_nh3_id = ""
        if html_request.form.get("gas_oxidising_id") is not None:
            self.gas_oxidised_id = html_request.form.get("gas_oxidising_id").strip()
        else:
            self.gas_oxidised_id = ""
        if html_request.form.get("gas_reducing_id") is not None:
            self.gas_reduced_id = html_request.form.get("gas_reducing_id").strip()
        else:
            self.gas_reduced_id = ""
        if html_request.form.get("pm1_id") is not None:
            self.pm1_id = html_request.form.get("pm1_id").strip()
        else:
            self.pm1_id = ""
        if html_request.form.get("pm2_5_id") is not None:
            self.pm2_5_id = html_request.form.get("pm2_5_id").strip()
        else:
            self.pm2_5_id = ""
        if html_request.form.get("pm10_id") is not None:
            self.pm10_id = html_request.form.get("pm10_id").strip()
        else:
            self.pm10_id = ""
        if html_request.form.get("lumen_id") is not None:
            self.lumen_id = html_request.form.get("lumen_id").strip()
        else:
            self.lumen_id = ""
        if html_request.form.get("red_id") is not None:
            self.red_id = html_request.form.get("red_id").strip()
        else:
            self.red_id = ""
        if html_request.form.get("orange_id") is not None:
            self.orange_id = html_request.form.get("orange_id").strip()
        else:
            self.orange_id = ""
        if html_request.form.get("yellow_id") is not None:
            self.yellow_id = html_request.form.get("yellow_id").strip()
        else:
            self.yellow_id = ""
        if html_request.form.get("green_id") is not None:
            self.green_id = html_request.form.get("green_id").strip()
        else:
            self.green_id = ""
        if html_request.form.get("blue_id") is not None:
            self.blue_id = html_request.form.get("blue_id").strip()
        else:
            self.blue_id = ""
        if html_request.form.get("violet_id") is not None:
            self.violet_id = html_request.form.get("violet_id").strip()
        else:
            self.violet_id = ""
        if html_request.form.get("uv_index_id") is not None:
            self.ultra_violet_index_id = html_request.form.get("uv_index_id").strip()
        else:
            self.ultra_violet_index_id = ""
        if html_request.form.get("uv_a_id") is not None:
            self.ultra_violet_a_id = html_request.form.get("uv_a_id").strip()
        else:
            self.ultra_violet_a_id = ""
        if html_request.form.get("uv_b_id") is not None:
            self.ultra_violet_b_id = html_request.form.get("uv_b_id").strip()
        else:
            self.ultra_violet_b_id = ""
        self.write_config_to_file()

    def update_settings_from_file(self, file_content=None, skip_write=False):
        """
        Updates Open Sense Map settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.osm_config) or skip_write:
            if file_content is None:
                loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.osm_config)
            else:
                loaded_configuration_raw = file_content
            configuration_lines = loaded_configuration_raw.split("\n")
            try:
                if int(configuration_lines[1][0]):
                    self.open_sense_map_enabled = 1
                else:
                    self.open_sense_map_enabled = 0

                self.sense_box_id = configuration_lines[2].split("=")[0].strip()

                try:
                    self.interval_seconds = float(configuration_lines[3].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Open Sense Map Interval Error from file - " + str(error))
                    self.interval_seconds = 900.0

                self.temperature_id = configuration_lines[4].split("=")[0].strip()
                self.pressure_id = configuration_lines[5].split("=")[0].strip()
                self.altitude_id = configuration_lines[6].split("=")[0].strip()
                self.humidity_id = configuration_lines[7].split("=")[0].strip()
                self.gas_voc_id = configuration_lines[8].split("=")[0].strip()
                self.gas_nh3_id = configuration_lines[9].split("=")[0].strip()
                self.gas_oxidised_id = configuration_lines[10].split("=")[0].strip()
                self.gas_reduced_id = configuration_lines[11].split("=")[0].strip()
                self.pm1_id = configuration_lines[12].split("=")[0].strip()
                self.pm2_5_id = configuration_lines[13].split("=")[0].strip()
                self.pm10_id = configuration_lines[14].split("=")[0].strip()
                self.lumen_id = configuration_lines[15].split("=")[0].strip()
                self.red_id = configuration_lines[16].split("=")[0].strip()
                self.orange_id = configuration_lines[17].split("=")[0].strip()
                self.yellow_id = configuration_lines[18].split("=")[0].strip()
                self.green_id = configuration_lines[19].split("=")[0].strip()
                self.blue_id = configuration_lines[20].split("=")[0].strip()
                self.violet_id = configuration_lines[21].split("=")[0].strip()
                self.ultra_violet_index_id = configuration_lines[22].split("=")[0].strip()
                self.ultra_violet_a_id = configuration_lines[23].split("=")[0].strip()
                self.ultra_violet_b_id = configuration_lines[24].split("=")[0].strip()
            except Exception as error:
                if not skip_write:
                    logger.primary_logger.warning("Problem loading Open Sense Map Configuration file - " +
                                                  "Using 1 or more Defaults: " + str(error))
                    self.write_config_to_file()
                else:
                    self.bad_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Open Sense Map Configuration file not found - Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Open Sense Map settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.osm_config, config_str)

    def start_open_sense_map(self):
        """ Sends compatible sensor readings to Open Sense Map every X seconds based on set Interval. """
        if not app_config_access.open_sense_map_thread_running and self.sense_box_id != "":
            app_config_access.open_sense_map_thread_running = True
            # Sleep 8 seconds before starting
            # So it doesn't try to access the sensors at the same time as the recording services on boot
            sleep(8)

            url = open_sense_map_main_url_start + "/" + self.sense_box_id + "/data"
            url_header = {"content-type": "application/json"}

            round_decimal_to = 5
            while True:
                body_json = {}
                try:
                    if app_config_access.installed_sensors.has_env_temperature:
                        if self.temperature_id != "":
                            try:
                                env_temperature = self.sensor_access.get_sensor_temperature()
                                if app_config_access.current_config.enable_custom_temp:
                                    env_temperature = round(env_temperature +
                                                            app_config_access.current_config.temperature_offset,
                                                            round_decimal_to)
                            except Exception as error:
                                logger.network_logger.warning("Open Sense Map: Env Temperature Error - " + str(error))
                                env_temperature = 0.0
                            body_json[self.temperature_id] = str(env_temperature)

                    if app_config_access.installed_sensors.has_pressure:
                        if self.pressure_id != "":
                            body_json[self.pressure_id] = str(self.sensor_access.get_pressure())
                    if app_config_access.installed_sensors.has_altitude:
                        if self.altitude_id != "":
                            body_json[self.altitude_id] = str(self.sensor_access.get_altitude())
                    if app_config_access.installed_sensors.has_humidity:
                        if self.humidity_id != "":
                            body_json[self.humidity_id] = str(self.sensor_access.get_humidity())
                    if app_config_access.installed_sensors.has_gas:
                        gas_voc = self.sensor_access.get_gas_resistance_index()
                        gas_oxidised = self.sensor_access.get_gas_oxidised()
                        gas_reduced = self.sensor_access.get_gas_reduced()
                        gas_nh3 = self.sensor_access.get_gas_nh3()
                        if self.gas_voc_id != "" and valid_sensor_reading(gas_voc):
                            body_json[self.gas_voc_id] = str(gas_voc)
                        if self.gas_oxidised_id != "" and valid_sensor_reading(gas_oxidised):
                            body_json[self.gas_oxidised_id] = str(gas_oxidised)
                        if self.gas_reduced_id != "" and valid_sensor_reading(gas_reduced):
                            body_json[self.gas_reduced_id] = str(gas_reduced)
                        if self.gas_nh3_id != "" and valid_sensor_reading(gas_nh3):
                            body_json[self.gas_nh3_id] = str(gas_nh3)
                    if app_config_access.installed_sensors.has_lumen:
                        if self.lumen_id != "":
                            body_json[self.lumen_id] = str(self.sensor_access.get_lumen())
                    if app_config_access.installed_sensors.has_particulate_matter:
                        pm1 = self.sensor_access.get_particulate_matter_1()
                        pm2_5 = self.sensor_access.get_particulate_matter_2_5()
                        pm10 = self.sensor_access.get_particulate_matter_10()
                        if self.pm1_id != "" and valid_sensor_reading(pm1):
                            body_json[self.pm1_id] = str(pm1)
                        if self.pm2_5_id != "" and valid_sensor_reading(pm2_5):
                            body_json[self.pm2_5_id] = str(pm2_5)
                        if self.pm10_id != "" and valid_sensor_reading(pm10):
                            body_json[self.pm10_id] = str(pm10)
                    colours = self.sensor_access.get_ems()
                    if app_config_access.installed_sensors.has_red:
                        if self.red_id != "":
                            body_json[self.red_id] = str(colours[0])
                    if app_config_access.installed_sensors.has_orange:
                        if self.orange_id != "":
                            body_json[self.orange_id] = str(colours[1])
                    if app_config_access.installed_sensors.has_yellow:
                        if self.yellow_id != "":
                            body_json[self.yellow_id] = str(colours[2])
                    if app_config_access.installed_sensors.has_green:
                        if self.green_id != "":
                            body_json[self.green_id] = str(colours[3])
                    if app_config_access.installed_sensors.has_blue:
                        if self.blue_id != "":
                            body_json[self.blue_id] = str(colours[4])
                    if app_config_access.installed_sensors.has_violet:
                        if self.violet_id != "":
                            body_json[self.violet_id] = str(colours[5])
                    if app_config_access.installed_sensors.has_ultra_violet:
                        if self.ultra_violet_index_id != "":
                            body_json[self.ultra_violet_index_id] = str(self.sensor_access.get_ultra_violet_index())
                        if self.ultra_violet_a_id != "":
                            body_json[self.ultra_violet_a_id] = str(self.sensor_access.get_ultra_violet_a())
                        if self.ultra_violet_b_id != "":
                            body_json[self.ultra_violet_b_id] = str(self.sensor_access.get_ultra_violet_b())

                    if len(body_json) > 0:
                        html_get_response = requests.post(url=url, headers=url_header, json=body_json)
                        if html_get_response.status_code == 201:
                            logger.network_logger.debug("Sensors sent to Open Sense Map OK")
                        elif html_get_response.status_code == 415:
                            logger.network_logger.error("Open Sense Map: - Invalid or Missing content type")
                        else:
                            logger.network_logger.error("Open Sense Map: Error " +
                                                        str(html_get_response.status_code) + " - " +
                                                        str(html_get_response.text))
                    else:
                        logger.network_logger.warning("Open Sense Map not Updated - " +
                                                      "No Compatible Sensors or Missing Sensor IDs")
                        while True:
                            sleep(3600)
                except Exception as error:
                    logger.network_logger.error("Error sending data to Open Sense Map")
                    logger.network_logger.debug("Open Sense Map Error: " + str(error))
                sleep(self.interval_seconds)

    def add_sensor_to_account(self, html_request):
        url = open_sense_map_main_url_start
        bad_location_message = "Open Sense Map: Sensor Registration - Invalid Location Setting"
        try:
            username = html_request.form.get("osm_account_username").strip()
            password = html_request.form.get("osm_account_password").strip()
            login_token = self.get_json_web_login_token(username, password)
            if login_token is not None:
                url_header = {"Authorization": "Bearer " + login_token,
                              "content-type": "application/json"}
                body_json = {"name": app_cached_variables.hostname,
                             "exposure": html_request.form.get("osm_location_type").strip()}

                grouptag = html_request.form.get("osm_grouptag").strip()
                if grouptag is not None and grouptag != "":
                    body_json["grouptag"] = grouptag
                location_extract = html_request.form.get("osm_location_coordinates").split(",")
                body_json["location"] = {"lat": float(location_extract[0].strip()),
                                         "lng": float(location_extract[1].strip()),
                                         "height": float(location_extract[2].strip())}
                body_json["sensors"] = self._get_osm_registration_sensors()

                html_get_response = requests.post(url=url, headers=url_header, json=body_json)
                if html_get_response.status_code == 201:
                    logger.network_logger.info("Registered Sensor on Open Sense Map OK")
                    return 201
                elif html_get_response.status_code == 415:
                    logger.network_logger.error("Open Sense Map: - Invalid or Missing content type")
                    return 415
                elif html_get_response.status_code == 422:
                    logger.network_logger.error(bad_location_message)
                    return 422
                else:
                    logger.network_logger.error("Open Sense Map Sensor Registration Error: " +
                                                str(html_get_response.status_code) + " - " +
                                                str(html_get_response.text))
                    return "UnknownError"
            else:
                logger.network_logger.error("Error Adding Sensor to Open Sense Map Account: Login Failed")
                return "FailedLogin"
        except IndexError:
            logger.network_logger.error(bad_location_message)
            return 422
        except ValueError:
            logger.network_logger.error(bad_location_message)
            return 422
        except Exception as error:
            logger.network_logger.error("Error Adding Sensor to Open Sense Map Account: " + str(error))
            return str(error)

    @staticmethod
    def _get_osm_registration_sensors():
        sensor_types = []
        if app_config_access.installed_sensors.raspberry_pi_sense_hat:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "RPiSenseHAT",
                "icon": "osem-thermometer"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "RPiSenseHAT",
                "icon": "osem-barometer"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "RPiSenseHAT",
                "icon": "osem-humidity"
            })
        if app_config_access.installed_sensors.pimoroni_enviro:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-thermometer"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-barometer"
            })
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT",
                "icon": "osem-brightness"
            })
        if app_config_access.installed_sensors.pimoroni_enviroplus:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniEnviroPlus",
                "icon": "osem-thermometer"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniEnviroPlus",
                "icon": "osem-barometer"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "PimoroniEnviroPlus",
                "icon": "osem-humidity"
            })
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPlus",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Oxidised",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Reduced",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "nh3",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
        if app_config_access.installed_sensors.pimoroni_pms5003:
            sensor_types.append({
                "title": "PM1",
                "unit": "µg/m³",
                "sensorType": "PSM5003",
                "icon": "osem-cloud"
            })
            sensor_types.append({
                "title": "PM2.5",
                "unit": "µg/m³",
                "sensorType": "PSM5003",
                "icon": "osem-cloud"
            })
            sensor_types.append({
                "title": "PM10",
                "unit": "µg/m³",
                "sensorType": "PSM5003",
                "icon": "osem-cloud"
            })
        if app_config_access.installed_sensors.pimoroni_bme680:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniBME680",
                "icon": "osem-thermometer"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniBME680",
                "icon": "osem-barometer"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "PimoroniBME680",
                "icon": "osem-humidity"
            })
            sensor_types.append({
                "title": "Gas VOC",
                "unit": "kΩ",
                "sensorType": "PimoroniBME680"
            })
        if app_config_access.installed_sensors.pimoroni_bmp280:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniBMP280",
                "icon": "osem-thermometer"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniBMP280",
                "icon": "osem-barometer"
            })
            sensor_types.append({
                "title": "Altitude",
                "unit": "m",
                "sensorType": "PimoroniBMP280"
            })
        if app_config_access.installed_sensors.pimoroni_ltr_559:
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniLTR559",
                "icon": "osem-brightness"
            })
        if app_config_access.installed_sensors.pimoroni_as7262:
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Orange",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Yellow",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Violet",
                "unit": "lm",
                "sensorType": "PimoroniAS7262",
                "icon": "osem-brightness"
            })
        if app_config_access.installed_sensors.pimoroni_bh1745:
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniBH1745",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniBH1745",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniBH1745",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniBH1745",
                "icon": "osem-brightness"
            })
        if app_config_access.installed_sensors.pimoroni_veml6075:
            sensor_types.append({
                "title": "UltraVioletIndex",
                "unit": "UV",
                "sensorType": "PimoroniVEML6075",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "UltraVioletA",
                "unit": "UVA",
                "sensorType": "PimoroniVEML6075",
                "icon": "osem-brightness"
            })
            sensor_types.append({
                "title": "UltraVioletB",
                "unit": "UVB",
                "sensorType": "PimoroniVEML6075",
                "icon": "osem-brightness"
            })
        return sensor_types

    @staticmethod
    def get_json_web_login_token(account_email, account_password):
        response = requests.post(url=open_sense_map_login_url,
                                 json={"email": account_email, "password": account_password})
        if response.status_code == 200:
            try:
                logger.network_logger.debug("Open Sense Map - Get Token: OK")
                return response.json()["token"]
            except Exception as error:
                logger.network_logger.warning("Open Sense Map - Get Token: Failed - " + str(error))
        elif response.status_code == 403:
            logger.network_logger.debug("Open Sense Map - Get Token: Login Failed")
        else:
            logger.network_logger.warning("Open Sense Map - Get Token: Login went wrong somehow...")
