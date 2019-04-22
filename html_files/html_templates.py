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


sensor_readings_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sensors Readings Report</title>
    <style>
        table {
            border: 3px solid white;
            border-collapse: collapse;
        }

        th, td {
            padding: 5px;
            white-space: nowrap;
        }

        th {
            text-align: left;
            white-space: nowrap;
        }

        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
</head>
<body><p>
<table>
"""

sensor_info_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sensors System Report</title>
    <style>
        table {
            border: 3px solid white;
            border-collapse: collapse;
        }

        th, td {
            padding: 5px;
            white-space: nowrap;
        }

        th {
            text-align: left;
            white-space: nowrap;
        }

        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
</head>
<body><p>
<table>
    <tr>
        <th><span style="background-color: #00ffff;">Sensor Name</span></th>
        <th><span style="background-color: #00ffff;">IP Address</span></th>
        <th><span style="background-color: #00ffff;">Sensor Time</span></th>
        <th><span style="background-color: #00ffff;">System UpTime (Minutes)</span></th>
        <th><span style="background-color: #00ffff;">Version</span></th>
        <th><span style="background-color: #00ffff;">CPU Temp</span></th>
        <th><span style="background-color: #00ffff;">Free Disk Space</span></th>
        <th><span style="background-color: #00ffff;">SQL DB Size</span></th>
        <th><span style="background-color: #00ffff;">Last Updated</span></th>
    </tr>
"""

sensor_config_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sensors Configuration Report</title>
    <style>
        table {
            border: 3px solid white;
            border-collapse: collapse;
        }

        th, td {
            padding: 5px;
            white-space: nowrap;
        }

        th {
            text-align: left;
            white-space: nowrap;
        }

        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
</head>
<body><p>
<table>
    <tr>
        <th><span style="background-color: #00ffff;">Interval to DB</span></th>
        <th><span style="background-color: #00ffff;">Trigger to DB</span></th>
        <th><span style="background-color: #00ffff;">Interval Duration</span></th>
        <th><span style="background-color: #00ffff;">Custom Temp Offset</span></th>
        <th><span style="background-color: #00ffff;">Temperature Offset</span></th>
        <th><span style="background-color: #00ffff;">Installed Sensors</span></th>
    </tr>
"""
