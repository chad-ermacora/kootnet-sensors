"""
This module is for the Pimoroni RV3028 Real-Time Clock
This will maintain time, even when power is out
(until the battery runs out on the RV3028)

RV3028 Real-Time Clock (RTC)
Ultra-low-power (~100nA typical current draw)
±1 second drift per million seconds at 25 degrees
Silver oxide battery included (1.55V, 8mAh, 337 type)
3.3V or 5V compatible
I2C interface (address 0x52)
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with all 40-pin Raspberry Pi models
Compatible with Arduino

pip3 install rv3028

Created on Thur Sept 9 13:23:56 2021

@author: OO-Dragon
"""
import os
import time
import datetime
import socket
import struct
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access

date_format = "%Y-%m-%d %H:%M:%S"
sleep_duration_between_datetime_checks = 18000  # Default is 18000 (5 Hours)


class CreateRV3028:
    """ Creates Function access to the Pimoroni RV3028. """

    def __init__(self):
        try:
            rv3028_import = __import__("sensor_modules.drivers.rv3028", fromlist=["RV3028"])
            self.real_time_clock = rv3028_import.RV3028()
            self.real_time_clock.set_battery_switchover('level_switching_mode')

            rtc_raw_datetime = self.get_time_from_rtc()
            logger.sensors_logger.info("Pimoroni RV3028 Currently Saved RTC Time: " + rtc_raw_datetime)

            self.thread_date_time_updater = Thread(target=self._rtc_check_thread)
            self.thread_date_time_updater.daemon = True
            self.thread_date_time_updater.start()

            logger.sensors_logger.debug("Pimoroni RV3028 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni RV3028 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_rv3028 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _rtc_check_thread(self):
        time.sleep(30)
        while True:
            # If NTP available (Internet access), use it first
            self._verify_with_ntp()
            try:
                rtc_raw_datetime = self.get_time_from_rtc()
                current_system_datetime = datetime.datetime.now()
                current_rtc_datetime = datetime.datetime.strptime(rtc_raw_datetime, date_format)
                time_difference = (current_system_datetime - current_rtc_datetime).total_seconds()

                logger.sensors_logger.debug("System Date & Time: " + current_system_datetime.strftime(date_format))
                logger.sensors_logger.debug("Pimoroni RV3028 DateTime: " + current_rtc_datetime.strftime(date_format))
                log_msg = "Pimoroni RV3028 - System/RTC time off by " + str(time_difference) + " seconds"
                logger.sensors_logger.debug(log_msg)

                if time_difference > 60.0:
                    self.update_rtc_time()
                elif time_difference < -60.0:
                    self.update_system_time()
                logger.sensors_logger.debug("Pimoroni RV3028 Date & Time Check Finished")
            except Exception as error:
                logger.sensors_logger.error("Pimoroni RV3028 Date & Time Check - Failed: " + str(error))
            time.sleep(sleep_duration_between_datetime_checks)

    def _verify_with_ntp(self):
        try:
            ntp_time = self.request_time_from_ntp()
            current_system_datetime = datetime.datetime.now()
            if ntp_time is None:
                logger.sensors_logger.debug("Pimoroni RV3028 - NTP Access Unavailable (No Internet?)")
            else:
                ntp_time = datetime.datetime.fromtimestamp(ntp_time)
                ntp_time_difference = (current_system_datetime - ntp_time).total_seconds()
                log_msg = "Pimoroni RV3028 - System/NTP time off by " + str(ntp_time_difference) + " seconds"
                logger.sensors_logger.debug(log_msg)
                if ntp_time_difference > 60.0 or ntp_time_difference < -60.0:
                    logger.sensors_logger.debug("Pimoroni RV3028 - Setting to NTP: " + ntp_time.strftime(date_format))
                    self.update_rtc_time(ntp_time)
                    self.update_system_time()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni RV3028 - NTP Verify: " + str(error))

    def update_rtc_time(self, date_and_time=datetime.datetime.now()):
        """
        Sets the RV3028 Real Time Clock to the System's current Date & Time

        Optional: date_and_time can be set manually
        Note: date_and_time may also be set as a tuple (hour, minute, second, year, month, date)
        """
        try:
            self.real_time_clock.set_time_and_date(date_and_time)
            logger.sensors_logger.debug("Pimoroni RV3028 - Update RTC to System's Date & Time - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni RV3028 - Update RTC to System's Date & Time Failed: " + str(error))

    def get_time_from_rtc(self):
        """
        Returns the Date & Time currently stored on the RV3028 Real Time Clock

        Format "2021-09-22 14:14:28" - Year/Month/Day hour:min:sec
        """
        try:
            rtc_time = self.real_time_clock.get_time_and_date()

            seconds = self._add_datetime_padding(str(rtc_time.second))
            minutes = self._add_datetime_padding(str(rtc_time.minute))
            hours = self._add_datetime_padding(str(rtc_time.hour))
            days = self._add_datetime_padding(str(rtc_time.day))
            months = self._add_datetime_padding(str(rtc_time.month))
            years = self._add_datetime_padding(str(rtc_time.year))

            return years + "-" + months + "-" + days + " " + hours + ":" + minutes + ":" + seconds
        except Exception as error:
            logger.sensors_logger.warning("Pimoroni RV3028 - Retrieving RTC's Date & Time: " + str(error))
        return "Error"

    @staticmethod
    def _add_datetime_padding(var):
        if len(var) < 2:
            return "0" + var
        return var

    def update_system_time(self):
        """ Sets the System's Date & Time using the RV3028 Real Time Clock """
        try:
            rtc_time = self.real_time_clock.get_time_and_date()
            # Linux date format is 2014-12-25 12:34:56 - Year-Month-Day hour:min:sec
            rtc_datetime = str(rtc_time.year) + "-" + str(rtc_time.month) + "-" + str(rtc_time.day) + " " + \
                           str(rtc_time.hour) + ":" + str(rtc_time.minute) + ":" + str(rtc_time.second)
            os.system("date -s '" + rtc_datetime + "'")
            logger.sensors_logger.debug("Pimoroni RV3028 - Update System's Date & Time to RTC's OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni RV3028 - Update System's Date & Time to RTC's Failed: " + str(error))

    @staticmethod
    def request_time_from_ntp(addr='pool.ntp.org', reference_time=2208988800):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = b'\x1b' + 47 * b'\0'
            client.sendto(data, (addr, 123))
            data, address = client.recvfrom(1024)
            t = reference_time
            if data:
                t = struct.unpack('!12I', data)[10]
                t -= reference_time
            return t
        except Exception as error:
            logger.sensors_logger.debug("Pimoroni RV3028 - NTP Check Failed: " + str(error))
        return None
