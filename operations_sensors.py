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

import operations_config
import operations_db
import sensor_modules.Linux_OS
import sensor_modules.Pimoroni_BH1745
import sensor_modules.Pimoroni_BME680
import sensor_modules.Pimoroni_Enviro
import sensor_modules.Pimoroni_LSM303D
import sensor_modules.Pimoroni_VL53L1X
import sensor_modules.RaspberryPi_SenseHAT
import sensor_modules.RaspberryPi_System

installed_sensors = operations_config.get_installed_sensors()
sense_hat_show_led_message = False


def get_interval_sensor_readings():
    """ Returns Interval sensor readings from installed sensors (set in installed sensors file). """
    interval_data = operations_db.CreateIntervalDatabaseData()
    interval_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    count = 0
    if installed_sensors.linux_system:
        sensor_os = sensor_modules.Linux_OS.CreateLinuxSystem()
        sensor_system = sensor_modules.RaspberryPi_System.CreateRPSystem()

        tmp_sensor_types = "SensorName, IP, SensorUpTime, SystemTemp"

        tmp_sensor_readings = "'" + str(sensor_os.get_hostname()) + "', '" + \
                              str(sensor_os.get_ip()) + "', '" + \
                              str(sensor_os.get_uptime()) + "', '" + \
                              str(sensor_system.cpu_temperature()) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        temperature = sensor_access.temperature()
        pressure = sensor_access.pressure()
        humidity = sensor_access.humidity()

        tmp_sensor_readings = "'" + str(temperature) + "', '" + \
                              str(pressure) + "', '" + \
                              str(humidity) + "'"

        if sense_hat_show_led_message:
            led_message = "SenseHAT " + str(int(temperature)) + "C " + str(pressure) + "hPa " + str(
                int(humidity)) + "%RH"
            sensor_access.display_led_message(led_message)

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.humidity()) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_bh1745:
        sensor_access = sensor_modules.Pimoroni_BH1745.CreateBH1745()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings

    return interval_data


def get_trigger_sensor_readings():
    """ Returns Trigger sensor readings from installed sensors (set in installed sensors file). """
    trigger_data = operations_db.CreateTriggerDatabaseData()
    trigger_data.sensor_readings = "'" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "', "

    count = 0
    if installed_sensors.linux_system:
        sensor_access = sensor_modules.Linux_OS.CreateLinuxSystem()

        sensor_types = "SensorName, IP"
        sensor_readings = "'" + str(sensor_access.get_hostname()) + "', '" + str(sensor_access.get_ip()) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X, Acc_Y, Acc_Z, Mag_X, Mag_Y, Mag_Z, Gyro_X, Gyro_Y, Gyro_Z"

        acc_x, acc_y, acc_z = sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = sensor_access.magnetometer_xyz()
        gyro_x, gyro_y, gyro_z = sensor_access.gyroscope_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "', '" + \
                          str(gyro_x) + "', '" + \
                          str(gyro_y) + "', '" + \
                          str(gyro_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        acc_x, acc_y, acc_z = sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        acc_x, acc_y, acc_z = sensor_access.accelerometer_xyz()
        mag_x, mag_y, mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(acc_x) + "', '" + \
                          str(acc_y) + "', '" + \
                          str(acc_z) + "', '" + \
                          str(mag_x) + "', '" + \
                          str(mag_y) + "', '" + \
                          str(mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings

    return trigger_data


def get_hostname():
    """ Returns sensors hostname. """
    if installed_sensors.linux_system:
        linux_os = sensor_modules.Linux_OS.CreateLinuxSystem()
        sensor_name = linux_os.get_hostname()
        return sensor_name
    else:
        return "NoSensor"


def get_system_uptime():
    """ Returns sensors system UpTime. """
    if installed_sensors.linux_system:
        linux_os = sensor_modules.Linux_OS.CreateLinuxSystem()
        sensor_uptime = linux_os.get_uptime()
        return sensor_uptime
    else:
        return "NoSensor"


def get_cpu_temperature():
    """ Returns sensors CPU temperature. """
    if installed_sensors.raspberry_pi:
        sensor_access = sensor_modules.RaspberryPi_System.CreateRPSystem()
        temperature = sensor_access.cpu_temperature()
        return temperature
    else:
        return "NoSensor"


def get_sensor_temperature():
    """ Returns sensors Environmental temperature. """
    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        temperature = sensor_access.temperature()
        return temperature
    elif installed_sensors.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()
        temperature = sensor_access.temperature()
        return temperature
    elif installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        temperature = sensor_access.temperature()
        return temperature
    else:
        return "NoSensor"


def get_pressure():
    """ Returns sensors pressure. """
    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        pressure = sensor_access.pressure()
        return pressure
    elif installed_sensors.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()
        pressure = sensor_access.pressure()
        return pressure
    elif installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        pressure = sensor_access.pressure()
        return pressure
    else:
        return "NoSensor"


def get_humidity():
    """ Returns sensors humidity. """
    if installed_sensors.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()
        humidity = sensor_access.humidity()
        return humidity
    elif installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        humidity = sensor_access.humidity()
        return humidity
    else:
        return "NoSensor"


def get_lumen():
    """ Returns sensors lumen. """
    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        lumen = sensor_access.lumen()
        return lumen
    elif installed_sensors.pimoroni_bh1745:
        sensor_access = sensor_modules.Pimoroni_BH1745.CreateBH1745()
        lumen = sensor_access.lumen()
        return lumen
    else:
        return "NoSensor"


def get_rgb():
    """ Returns sensors Red, Green, Blue spectrum. """
    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        rgb = sensor_access.rgb()
        return rgb
    elif installed_sensors.pimoroni_bh1745:
        sensor_access = sensor_modules.Pimoroni_BH1745.CreateBH1745()
        rgb = sensor_access.rgb()
        return rgb
    else:
        return "NoSensor"


def get_accelerometer_xyz():
    """ Returns sensors Accelerometer XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        xyz = sensor_access.accelerometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        xyz = sensor_access.accelerometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()
        xyz = sensor_access.accelerometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_magnetometer_xyz():
    """ Returns sensors Magnetometer XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        xyz = sensor_access.magnetometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()
        xyz = sensor_access.magnetometer_xyz()
        return xyz
    elif installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()
        xyz = sensor_access.magnetometer_xyz()
        return xyz
    else:
        return "NoSensor"


def get_gyroscope_xyz():
    """ Returns sensors Gyroscope XYZ. """
    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
        xyz = sensor_access.gyroscope_xyz()
        return xyz
    else:
        return "NoSensor"
