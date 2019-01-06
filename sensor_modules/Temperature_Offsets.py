"""
This module holds Environmental Temperature offsets based on hardware

@author: OO-Dragon
"""
from operations_modules.operations_config import current_config, installed_sensors


class CreateRPZeroWTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -0.0  # Preliminary Testing
        self.pimoroni_enviro = -4.5  # Tested
        self.rp_sense_hat = -5.5  # Untested, guessing


class CreateRP3BPlusTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -2.5  # Tested when Raspberry Pi is on its side
        self.pimoroni_enviro = -6.5  # Untested, guessing
        self.rp_sense_hat = -7.0  # Preliminary testing done


class CreateUnknownTemperatureOffsets:
    def __init__(self):
        # No Offset if unknown or unselected
        self.pimoroni_bme680 = 0.0
        self.pimoroni_enviro = 0.0
        self.rp_sense_hat = 0.0


def get_sensor_temperature_offset():
    """
     Returns sensors Environmental temperature offset based on system board and sensor.
     You can set an override in the main sensor configuration file.
    """

    if installed_sensors.raspberry_pi_3b_plus:
        sensor_temp_offset = CreateRP3BPlusTemperatureOffsets()
    elif installed_sensors.raspberry_pi_zero_w:
        sensor_temp_offset = CreateRPZeroWTemperatureOffsets()
    else:
        # All offsets are 0.0 for unselected or unsupported system boards
        sensor_temp_offset = CreateUnknownTemperatureOffsets()

    if current_config.enable_custom_temp:
        return current_config.custom_temperature_offset
    elif installed_sensors.pimoroni_enviro:
        return sensor_temp_offset.pimoroni_enviro
    elif installed_sensors.pimoroni_bme680:
        return sensor_temp_offset.pimoroni_bme680
    elif installed_sensors.raspberry_pi_sense_hat:
        return sensor_temp_offset.rp_sense_hat
    else:
        return 0.0
