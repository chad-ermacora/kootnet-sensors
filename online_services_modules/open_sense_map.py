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
import requests
from time import sleep
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import CreateMonitoredThread
from configuration_modules.app_config_access import installed_sensors, open_sense_map_config as osm_config
from online_services_modules.osm_sensor_templates import pimoroni_enviro_plus, sensirion_sps30, pimoroni_as7262, \
    pimoroni_enviro, pimoroni_ltr_559, pimoroni_bmp280, raspberry_pi_sense_hat, pimoroni_bme680, pimoroni_veml6075, \
    pimoroni_pms5003, pimoroni_bh1745
from sensor_modules import sensor_access


db_v = app_cached_variables.database_variables


def start_open_sense_map_server():
    if osm_config.open_sense_map_enabled:
        text_name = "Open Sense Map"
        function = _open_sense_map_server
        app_cached_variables.open_sense_map_thread = CreateMonitoredThread(function, thread_name=text_name)
    else:
        logger.primary_logger.debug("Open Sense Map Disabled in Configuration")


def _open_sense_map_server():
    """ Sends compatible sensor readings to Open Sense Map every X seconds based on set Interval. """
    app_cached_variables.restart_open_sense_map_thread = False
    if osm_config.sense_box_id != "":
        url = osm_config.open_sense_map_main_url_start + "/" + osm_config.sense_box_id + "/data"
        url_header = {"content-type": "application/json"}

        while not app_cached_variables.restart_open_sense_map_thread:
            body_json = {}
            try:
                env_temperature = sensor_access.get_environment_temperature()
                if env_temperature is not None and osm_config.temperature_id != "":
                    body_json[osm_config.temperature_id] = env_temperature[db_v.env_temperature]

                pressure_reading = sensor_access.get_pressure()
                if pressure_reading is not None and osm_config.pressure_id != "":
                    body_json[osm_config.pressure_id] = pressure_reading[db_v.pressure]

                altitude_reading = sensor_access.get_altitude()
                if altitude_reading is not None and osm_config.altitude_id != "":
                    body_json[osm_config.altitude_id] = altitude_reading[db_v.altitude]

                humidity_reading = sensor_access.get_humidity()
                if humidity_reading is not None and osm_config.humidity_id != "":
                    body_json[osm_config.humidity_id] = humidity_reading[db_v.humidity]

                gas_readings = sensor_access.get_gas()
                if gas_readings is not None:
                    if db_v.gas_resistance_index in gas_readings and osm_config.gas_voc_id != "":
                        gas_voc = gas_readings[db_v.gas_resistance_index]
                        body_json[osm_config.gas_voc_id] = gas_voc
                    if db_v.gas_oxidising in gas_readings and osm_config.gas_oxidised_id != "":
                        gas_oxidised = gas_readings[db_v.gas_oxidising]
                        body_json[osm_config.gas_oxidised_id] = gas_oxidised
                    if db_v.gas_reducing in gas_readings and osm_config.gas_reduced_id != "":
                        gas_reduced = gas_readings[db_v.gas_reducing]
                        body_json[osm_config.gas_reduced_id] = gas_reduced
                    if db_v.gas_nh3 in gas_readings and osm_config.gas_nh3_id != "":
                        gas_nh3 = gas_readings[db_v.gas_nh3]
                        body_json[osm_config.gas_nh3_id] = gas_nh3

                lumen_reading = sensor_access.get_lumen()
                if lumen_reading is not None and osm_config.lumen_id != "":
                    body_json[osm_config.lumen_id] = lumen_reading[db_v.lumen]

                pm_readings = sensor_access.get_particulate_matter()
                if pm_readings is not None:
                    if db_v.particulate_matter_1 in pm_readings and osm_config.pm1_id != "":
                        pm1 = pm_readings[db_v.particulate_matter_1]
                        body_json[osm_config.pm1_id] = pm1
                    if db_v.particulate_matter_2_5 in pm_readings and osm_config.pm2_5_id != "":
                        pm2_5 = pm_readings[db_v.particulate_matter_2_5]
                        body_json[osm_config.pm2_5_id] = pm2_5
                    if db_v.particulate_matter_4 in pm_readings and osm_config.pm4_id != "":
                        pm4 = pm_readings[db_v.particulate_matter_4]
                        body_json[osm_config.pm4_id] = pm4
                    if db_v.particulate_matter_10 in pm_readings and osm_config.pm10_id != "":
                        pm10 = pm_readings[db_v.particulate_matter_10]
                        body_json[osm_config.pm10_id] = pm10

                colors = sensor_access.get_ems_colors()
                if colors is not None:
                    if db_v.red in colors and osm_config.red_id != "":
                        red = colors[db_v.red]
                        body_json[osm_config.red_id] = red
                    if db_v.orange in colors and osm_config.orange_id != "":
                        orange = colors[db_v.orange]
                        body_json[osm_config.orange_id] = orange
                    if db_v.yellow in colors and osm_config.yellow_id != "":
                        yellow = colors[db_v.yellow]
                        body_json[osm_config.yellow_id] = yellow
                    if db_v.green in colors and osm_config.green_id != "":
                        green = colors[db_v.green]
                        body_json[osm_config.green_id] = green
                    if db_v.blue in colors and osm_config.blue_id != "":
                        blue = colors[db_v.blue]
                        body_json[osm_config.blue_id] = blue
                    if db_v.violet in colors and osm_config.violet_id != "":
                        violet = colors[db_v.violet]
                        body_json[osm_config.violet_id] = violet

                uv_readings = sensor_access.get_ultra_violet()
                if uv_readings is not None:
                    if db_v.ultra_violet_index in uv_readings and osm_config.ultra_violet_index_id != "":
                        uv_index = uv_readings[db_v.ultra_violet_index]
                        body_json[osm_config.ultra_violet_index_id] = uv_index
                    if db_v.ultra_violet_a in uv_readings and osm_config.ultra_violet_a_id != "":
                        uv_a = uv_readings[db_v.ultra_violet_a]
                        body_json[osm_config.ultra_violet_a_id] = uv_a
                    if db_v.ultra_violet_b in uv_readings and osm_config.ultra_violet_b_id != "":
                        uv_b = uv_readings[db_v.ultra_violet_b]
                        body_json[osm_config.ultra_violet_b_id] = uv_b

                if len(body_json) > 0:
                    html_get_response = requests.post(url=url, headers=url_header, json=body_json)
                    status_code = str(html_get_response.status_code)
                    response_text = str(html_get_response.text)
                    if html_get_response.status_code == 201:
                        logger.network_logger.debug("Open Sense Map - Sent OK - Status Code: " + status_code)
                    elif html_get_response.status_code == 415:
                        logger.network_logger.error("Open Sense Map: Invalid or Missing content type")
                    else:
                        log_msg = "Open Sense Map - Unknown Error " + status_code + ": " + response_text
                        logger.network_logger.error(log_msg)
                else:
                    log_msg = "Open Sense Map - No further updates will be attempted: " + \
                              "No Compatible Sensors or Missing Sensor IDs"
                    logger.network_logger.warning(log_msg)
                    while not app_cached_variables.restart_open_sense_map_thread:
                        sleep(5)
            except Exception as error:
                logger.network_logger.error("Open Sense Map - Error sending data")
                logger.network_logger.debug("Open Sense Map - Detailed Error: " + str(error))

            sleep_fraction_interval = 5
            sleep_total = 0
            while sleep_total < osm_config.interval_seconds and not app_cached_variables.restart_open_sense_map_thread:
                sleep(sleep_fraction_interval)
                sleep_total += sleep_fraction_interval


def add_sensor_to_account(html_request):
    url = osm_config.open_sense_map_main_url_start
    bad_location_message = "Open Sense Map - Sensor Registration: Invalid Location Setting"
    try:
        username = html_request.form.get("osm_account_username").strip()
        password = html_request.form.get("osm_account_password").strip()
        login_token = get_json_web_login_token(username, password)
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
            body_json["sensors"] = _get_osm_registration_sensors()

            html_get_response = requests.post(url=url, headers=url_header, json=body_json)
            if html_get_response.status_code == 201:
                logger.network_logger.info("Registered Sensor on Open Sense Map OK")
                return 201
            elif html_get_response.status_code == 415:
                logger.network_logger.error("Open Sense Map error: Invalid or Missing content type")
                return 415
            elif html_get_response.status_code == 422:
                logger.network_logger.error(bad_location_message)
                return 422
            else:
                status_code = str(html_get_response.status_code)
                response_text = str(html_get_response.text)
                log_msg = "Open Sense Map - Sensor Registration Unknown Error " + status_code + ": " + response_text
                logger.network_logger.error(log_msg)
                return "UnknownError"
        else:
            logger.network_logger.error("Open Sense Map - Error Adding Sensor to Account: Login Failed")
            return "FailedLogin"
    except IndexError:
        logger.network_logger.error(bad_location_message)
        return 422
    except ValueError:
        logger.network_logger.error(bad_location_message)
        return 422
    except Exception as error:
        logger.network_logger.error("Open Sense Map - Error Adding Sensor to Account: " + str(error))
        return str(error)


def _get_osm_registration_sensors():
    sensor_types = []
    if installed_sensors.raspberry_pi_sense_hat:
        sensor_types += raspberry_pi_sense_hat.get_osm_sensor_template()
    if installed_sensors.pimoroni_enviro:
        sensor_types += pimoroni_enviro.get_osm_sensor_template()
    if installed_sensors.pimoroni_enviroplus:
        sensor_types += pimoroni_enviro_plus.get_osm_sensor_template()
    if installed_sensors.pimoroni_pms5003:
        sensor_types += pimoroni_pms5003.get_osm_sensor_template()
    if installed_sensors.sensirion_sps30:
        sensor_types += sensirion_sps30.get_osm_sensor_template()
    if installed_sensors.pimoroni_bme680:
        sensor_types += pimoroni_bme680.get_osm_sensor_template()
    if installed_sensors.pimoroni_bmp280:
        sensor_types += pimoroni_bmp280.get_osm_sensor_template()
    if installed_sensors.pimoroni_ltr_559:
        sensor_types += pimoroni_ltr_559.get_osm_sensor_template()
    if installed_sensors.pimoroni_as7262:
        sensor_types += pimoroni_as7262.get_osm_sensor_template()
    if installed_sensors.pimoroni_bh1745:
        sensor_types += pimoroni_bh1745.get_osm_sensor_template()
    if installed_sensors.pimoroni_veml6075:
        sensor_types += pimoroni_veml6075.get_osm_sensor_template()
    return sensor_types


def get_json_web_login_token(account_email, account_password):
    response = requests.post(url=osm_config.open_sense_map_login_url,
                             json={"email": account_email, "password": account_password})
    if response.status_code == 200:
        try:
            logger.network_logger.debug("Open Sense Map - Get Token: OK")
            return response.json()["token"]
        except Exception as error:
            logger.network_logger.warning("Open Sense Map - Get Token Failed: " + str(error))
    elif response.status_code == 403:
        logger.network_logger.debug("Open Sense Map - Get Token: Login Failed")
    else:
        logger.network_logger.warning("Open Sense Map - Get Token: Login went wrong somehow ...")
