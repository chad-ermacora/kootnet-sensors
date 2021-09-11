"""
This module is for the Pimoroni PA1010D GPS
It Retrieves & Returns GPS data to be written to the DB

PA1010D GPS / GLONASS / GALILEO receiver module with inbuilt ceramic antenna (datasheet)
Supports up to 210 PRN channels with 99 search channels and 33 simultaneous tracking channels
Ultra-high sensitivity: -165dBm
High accuracy 1-PPS timing support (±20ns jitter)

Super capacitor, which saves satellite locations and status in the event of a power down.
It also lets the GPS module run its internal clock, with about 1 hour of 'battery capacity'.

Green LED indicator, connected to the PPS output of the GPS module.
It's possible to disable the LED (or change the PPS output behaviour) with software.

2x M2.5 mounting holes
I2C interface, with a default address of 0x10
3V to 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with all models of Raspberry Pi.
Compatible with Arduino.

pip3 install pa1010d

Created on Sat Sept 11 11:07:56 2021

@author: OO-Dragon
"""
import time
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access

sleep_between_readings_seconds = 30


class CreatePA1010D:
    """ Creates Function access to the Pimoroni PA1010D. """

    def __init__(self):
        self.sensor_latency = 0.0

        self.timestamp = None
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.number_of_connected_satellites = None
        self.gps_quality = None

        self.pdop = None
        self.hdop = None
        self.vdop = None

        self.speed_over_ground = None
        self.mode_fix_type = None

        try:
            pa1010d_import = __import__("sensor_modules.drivers.pa1010d", fromlist=["PA1010D"])
            self.pa1010d_gps = pa1010d_import.PA1010D()
            self.pa1010d_gps.update()

            self.thread_gps_updater = Thread(target=self._gps_updater_thread)
            self.thread_gps_updater.daemon = True
            self.thread_gps_updater.start()

            logger.sensors_logger.debug("Pimoroni PA1010D Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni PA1010D Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_pa1010d = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _gps_updater_thread(self):
        # Give GPS time to lock on to a few satellites
        time.sleep(30)

        set_new_start_time = False
        start_time = time.time()
        while True:
            if set_new_start_time:
                set_new_start_time = False
                start_time = time.time()
            try:
                result = self.pa1010d_gps.update()
                if result:
                    end_time = time.time()
                    self.sensor_latency = float(end_time - start_time)
                    set_new_start_time = True

                    self.timestamp = str(self.pa1010d_gps.timestamp)
                    self.latitude = self.pa1010d_gps.latitude
                    self.longitude = self.pa1010d_gps.longitude
                    self.altitude = self.pa1010d_gps.altitude
                    self.number_of_connected_satellites = self.pa1010d_gps.number_of_connected_satellites
                    self.gps_quality = self.pa1010d_gps.gps_quality

                    self.pdop = self.pa1010d_gps.pdop
                    self.hdop = self.pa1010d_gps.hdop
                    self.vdop = self.pa1010d_gps.vdop

                    self.speed_over_ground = self.pa1010d_gps.speed_over_ground
                    self.mode_fix_type = self.pa1010d_gps.mode_fix_type

                    gps_log_str = "GPS Data - TimeStamp: " + str(self.timestamp) + \
                                  " Latitude: " + str(self.latitude) + \
                                  " Longitude: " + str(self.longitude) + \
                                  " Altitude: " + str(self.altitude) + \
                                  " Number of Sats: " + str(self.number_of_connected_satellites) + \
                                  " GPS Quality: " + str(self.gps_quality) + \
                                  " Speed Over Ground: " + str(self.speed_over_ground) + \
                                  " Mode Fix Type: " + str(self.mode_fix_type)
                    logger.sensors_logger.info(gps_log_str)
                    logger.sensors_logger.info("DOPs: " + str(self.pdop) + " " + str(self.hdop) + " " + str(self.vdop))
                    logger.sensors_logger.debug("Pimoroni PA1010D GPS Update Finished")
                else:
                    time.sleep(10)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni PA1010D GPS Update - Failed: " + str(error))
            time.sleep(sleep_between_readings_seconds)

    def get_latitude_longitude(self):
        """ Returns latitude & longitude coordinates (floats) in a list """
        return [self.latitude, self.longitude]

    def get_altitude(self):
        """ Returns altitude as a float """
        return self.altitude

    def get_number_of_satellites(self):
        """ Returns number of satellites as a int """
        return self.number_of_connected_satellites

    def get_gps_quality(self):
        """ Returns GPS Connection Quality as a int """
        return self.gps_quality

    def get_gps_timestamp(self):
        """ Returns GPS Timestamp as a string """
        return self.timestamp

    def get_gps_mode_fix_type(self):
        """ Returns GPS Mode Fix Type as a int """
        return self.mode_fix_type

    def get_speed_over_ground(self):
        """ Returns GPS Speed Over Ground as a float """
        return self.speed_over_ground

    def get_gps_pdop_hdop_vdop(self):
        """ Returns GPS PDOP, HDOP & VDOP (floats) as a list """
        return [self.pdop, self.hdop, self.vdop]

    def get_all_gps_data(self):
        """
        Returns latitude, longitude, altitude, time stamp, number of satellites, GPS quality,
        'mode fix type', speed over ground, PDOP, HDOP & VDOP in a list
        """
        return [self.latitude, self.longitude, self.altitude, self.timestamp,
                self.number_of_connected_satellites, self.gps_quality, self.mode_fix_type,
                self.speed_over_ground, self.pdop, self.hdop, self.vdop]
