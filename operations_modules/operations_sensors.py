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
from datetime import datetime

from operations_modules import operations_db
from sensor_modules import linux_os
from sensor_modules import pimoroni_as7262
from sensor_modules import pimoroni_bh1745
from sensor_modules import pimoroni_bme680
from sensor_modules import pimoroni_enviro
from sensor_modules import pimoroni_lsm303d
from sensor_modules import pimoroni_ltr_559
from sensor_modules import pimoroni_vl53l1x
from sensor_modules import raspberry_pi_sensehat
from sensor_modules import raspberry_pi_system
from operations_modules.operations_config import get_installed_sensors, \
    get_installed_config, \
    get_sensor_temperature_offset, \
    get_old_version, version

if get_old_version() == version:
    # Initialize sensor access, based on installed sensors file
    installed_sensors = get_installed_sensors()
    current_config = get_installed_config()
    if installed_sensors.linux_system:
        os_sensor_access = linux_os.CreateLinuxSystem()
    if installed_sensors.raspberry_pi_zero_w or installed_sensors.raspberry_pi_3b_plus:
        system_sensor_access = raspberry_pi_system.CreateRPSystem()
    if installed_sensors.raspberry_pi_sense_hat:
        rp_sense_hat_sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
    if installed_sensors.pimoroni_bh1745:
        pimoroni_bh1745_sensor_access = pimoroni_bh1745.CreateBH1745()
    if installed_sensors.pimoroni_as7262:
        pimoroni_as7262_sensor_access = pimoroni_as7262.CreateAS7262()
    if installed_sensors.pimoroni_bme680:
        pimoroni_bme680_sensor_access = pimoroni_bme680.CreateBME680()
    if installed_sensors.pimoroni_enviro:
        pimoroni_enviro_sensor_access = pimoroni_enviro.CreateEnviro()
    if installed_sensors.pimoroni_lsm303d:
        pimoroni_lsm303d_sensor_access = pimoroni_lsm303d.CreateLSM303D()
    if installed_sensors.pimoroni_ltr_559:
        pimoroni_ltr_559_sensor_access = pimoroni_ltr_559.CreateLTR559()
    if installed_sensors.pimoroni_vl53l1x:
        pimoroni_vl53l1x_sensor_access = pimoroni_vl53l1x.CreateVL53L1X()
else:
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    pass


def get_interval_sensor_readings():
    """ Returns Interval sensor readings from installed sensors (set in installed sensors file). """
    interval_data = operations_db.CreateIntervalDatabaseData()

    interval_data.sensor_types = "DateTime, "
    interval_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if installed_sensors.linux_system:
        interval_data.sensor_types += "SensorName, IP, SensorUpTime, SystemTemp, "

        if installed_sensors.raspberry_pi_3b_plus or installed_sensors.raspberry_pi_zero_w:
            cpu_temp = str(system_sensor_access.cpu_temperature())
        else:
            cpu_temp = None

        interval_data.sensor_readings += "'" + str(os_sensor_access.get_hostname()) + "', '" + \
                                         str(os_sensor_access.get_ip()) + "', '" + \
                                         str(os_sensor_access.get_uptime()) + "', '" + \
                                         cpu_temp + "', "

    if installed_sensors.raspberry_pi_sense_hat:
        interval_data.sensor_types += "EnvironmentTemp, " \
                                      "EnvTempOffset, " \
                                      "Pressure, " \
                                      "Humidity, "
        interval_data.sensor_readings += "'" + str(rp_sense_hat_sensor_access.temperature()) + "', '" + \
                                         str(get_sensor_temperature_offset()) + "', '" + \
                                         str(rp_sense_hat_sensor_access.pressure()) + "', '" + \
                                         str(rp_sense_hat_sensor_access.humidity()) + "', "

    if installed_sensors.pimoroni_bh1745:
        rgb_colour = pimoroni_bh1745_sensor_access.ems()

        interval_data.sensor_types += "Lumen, Red, Green, Blue, "
        interval_data.sensor_readings += "'" + str(pimoroni_bh1745_sensor_access.lumen()) + "', '" + \
                                         str(rgb_colour[0]) + "', '" + \
                                         str(rgb_colour[1]) + "', '" + \
                                         str(rgb_colour[2]) + "', "
    if installed_sensors.pimoroni_as7262:
        ems_colors = pimoroni_as7262_sensor_access.spectral_six_channel()

        interval_data.sensor_types += "Red, Orange, Yellow, Green, Blue, Violet, "
        interval_data.sensor_readings += "'" + str(ems_colors[0]) + "', '" + \
                                         str(ems_colors[1]) + "', '" + \
                                         str(ems_colors[2]) + "', '" + \
                                         str(ems_colors[3]) + "', '" + \
                                         str(ems_colors[4]) + "', '" + \
                                         str(ems_colors[5]) + "', "

    if installed_sensors.pimoroni_bme680:
        interval_data.sensor_types += "EnvironmentTemp, EnvTempOffset, Pressure, Humidity, "

        interval_data.sensor_readings += "'" + str(pimoroni_bme680_sensor_access.temperature()) + "', '" + \
                                         str(get_sensor_temperature_offset()) + "', '" + \
                                         str(pimoroni_bme680_sensor_access.pressure()) + "', '" + \
                                         str(pimoroni_bme680_sensor_access.humidity()) + "', "

    if installed_sensors.pimoroni_enviro:
        rgb_colour = pimoroni_enviro_sensor_access.ems()

        interval_data.sensor_types += \
            "EnvironmentTemp, " \
            "EnvTempOffset, " \
            "Pressure, " \
            "Lumen, " \
            "Red, " \
            "Green, " \
            "Blue, "
        interval_data.sensor_readings += "'" + str(pimoroni_enviro_sensor_access.temperature()) + "', '" + \
                                         str(get_sensor_temperature_offset()) + "', '" + \
                                         str(pimoroni_enviro_sensor_access.pressure()) + "', '" + \
                                         str(pimoroni_enviro_sensor_access.lumen()) + "', '" + \
                                         str(rgb_colour[0]) + "', '" + \
                                         str(rgb_colour[1]) + "', '" + \
                                         str(rgb_colour[2]) + "', "

    if installed_sensors.pimoroni_ltr_559:
        interval_data.sensor_types += "Lumen, "
        interval_data.sensor_readings += "'" + str(pimoroni_ltr_559_sensor_access.lumen()) + "', "

    interval_data.sensor_types = interval_data.sensor_types[:-2]
    interval_data.sensor_readings = interval_data.sensor_readings[:-2]

    if interval_data.sensor_types != "DateTime":
        return interval_data


def get_trigger_sensor_readings():
    """ Returns Trigger sensor readings from installed sensors (set in installed sensors file). """
    trigger_data = operations_db.CreateTriggerDatabaseData()
    trigger_data.sensor_types = "DateTime, "
    trigger_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    if installed_sensors.linux_system:
        sensor_types = "SensorName, IP, "
        sensor_readings = "'" + str(os_sensor_access.get_hostname()) + "', '" + str(os_sensor_access.get_ip()) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_types = "Acc_X, Acc_Y, Acc_Z, Mag_X, Mag_Y, Mag_Z, Gyro_X, Gyro_Y, Gyro_Z, "

        acc_x, acc_y, acc_z = rp_sense_hat_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = rp_sense_hat_sensor_access.magnetometer_xyz()
        gyro_x, gyro_y, gyro_z = rp_sense_hat_sensor_access.gyroscope_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', '" + \
                          str(gyro_x) + "', '" + \
                          str(gyro_y) + "', '" + \
                          str(gyro_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if installed_sensors.pimoroni_enviro:
        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        acc_x, acc_y, acc_z = pimoroni_enviro_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_enviro_sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    if installed_sensors.pimoroni_lsm303d:
        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, "

        acc_x, acc_y, acc_z = pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = pimoroni_lsm303d_sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', "

        trigger_data.sensor_types += sensor_types
        trigger_data.sensor_readings += sensor_readings

    trigger_data.sensor_types = trigger_data.sensor_types[:-2]
    trigger_data.sensor_readings = trigger_data.sensor_readings[:-2]

    if trigger_data.sensor_types != "DateTime":
        return trigger_data


def get_hostname():
    """ Returns sensors hostname. """
    if installed_sensors.linux_system:
        sensor_name = os_sensor_access.get_hostname()
        return sensor_name
    else:
        return "NoSensor"


def get_system_uptime():
    """ Returns sensors system UpTime. """
    if installed_sensors.linux_system:
        sensor_uptime = os_sensor_access.get_uptime()
        return sensor_uptime
    else:
        return "NoSensor"


def get_cpu_temperature():
    """ Returns sensors CPU temperature. """
    if installed_sensors.raspberry_pi_zero_w or installed_sensors.raspberry_pi_3b_plus:
        temperature = system_sensor_access.cpu_temperature()
        return temperature
    else:
        return "NoSensor"


def get_sensor_temperature():
    """ Returns sensors Environmental temperature. """
    if installed_sensors.pimoroni_enviro:
        temperature = pimoroni_enviro_sensor_access.temperature()
        return temperature
    elif installed_sensors.pimoroni_bme680:
        temperature = pimoroni_bme680_sensor_access.temperature()
        return temperature
    elif installed_sensors.raspberry_pi_sense_hat:
        temperature = rp_sense_hat_sensor_access.temperature()
        return temperature
    else:
        return "NoSensor"


def get_pressure():
    """ Returns sensors pressure. """
    if installed_sensors.pimoroni_enviro:
        pressure = pimoroni_enviro_sensor_access.pressure()
        return pressure
    elif installed_sensors.pimoroni_bme680:
        pressure = pimoroni_bme680_sensor_access.pressure()
        return pressure
    elif installed_sensors.raspberry_pi_sense_hat:
        pressure = rp_sense_hat_sensor_access.pressure()
        return pressure
    else:
        return "NoSensor"


def get_humidity():
    """ Returns sensors humidity. """
    if installed_sensors.pimoroni_bme680:
        humidity = pimoroni_bme680_sensor_access.humidity()
        return humidity
    elif installed_sensors.raspberry_pi_sense_hat:
        humidity = rp_sense_hat_sensor_access.humidity()
        return humidity
    else:
        return "NoSensor"


def get_lumen():
    """ Returns sensors lumen. """
    if installed_sensors.pimoroni_enviro:
        lumen = pimoroni_enviro_sensor_access.lumen()
        return lumen
    elif installed_sensors.pimoroni_bh1745:
        lumen = pimoroni_bh1745_sensor_access.lumen()
        return lumen
    elif installed_sensors.pimoroni_ltr_559:
        lumen = pimoroni_ltr_559_sensor_access.lumen()
        return lumen
    else:
        return "NoSensor"


def get_ems():
    """ Returns Electromagnetic Spectrum Wavelengths in the form of Red, Orange, Yellow, Green, Cyan, Blue, Violet. """
    if installed_sensors.pimoroni_enviro:
        rgb = pimoroni_enviro_sensor_access.ems()
        return rgb
    elif installed_sensors.pimoroni_bh1745:
        rgb = pimoroni_bh1745_sensor_access.ems()
        return rgb
    elif installed_sensors.pimoroni_as7262:
        six_chan = pimoroni_as7262_sensor_access.spectral_six_channel()
        return six_chan
    else:
        return "NoSensor"


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.accelerometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_enviro:
        xyz = pimoroni_enviro_sensor_access.accelerometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_lsm303d:
        xyz = pimoroni_lsm303d_sensor_access.accelerometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.magnetometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_enviro:
        xyz = pimoroni_enviro_sensor_access.magnetometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_lsm303d:
        xyz = pimoroni_lsm303d_sensor_access.magnetometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        xyz = rp_sense_hat_sensor_access.gyroscope_xyz()
        return xyz
    else:
        return "NoSensor"
