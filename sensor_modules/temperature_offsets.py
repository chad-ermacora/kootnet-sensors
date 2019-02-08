"""
This module holds Environmental Temperature offsets based on hardware

@author: OO-Dragon
"""


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
