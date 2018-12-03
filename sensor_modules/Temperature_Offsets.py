"""
This module holds Environmental Temperature offsets based on hardware

@author: OO-Dragon
"""


class CreateRPZeroWTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -0.0  # Tested
        self.pimoroni_enviro = -4.5  # Tested
        self.rp_sense_hat = -5.5  # Untested, guessing

        self.optional_pure_leaf_square = -2.5  # Tested on Enviro only


class CreateRP3BPlusTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -2.5  # Tested when Raspberry Pi is on its side
        self.pimoroni_enviro = -6.5  # Untested, guessing
        self.rp_sense_hat = -7.0  # Preliminary testing done

        self.optional_pure_leaf_square = -6.0  # Tested with SenseHAT only
