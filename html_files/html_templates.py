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

    This file contains HTML code used in locally provided HTML pages.
"""


# page_quick.py HTML page components
quick_page_title_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Local Sensor Management</title>
    <style>
        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
</head>
<body>
<h1><strong><span style="text-decoration: underline;">
<a href='/Quick' style='color: red'>Kootnet Sensor: 
"""

quick_page_title_end = "</a></span></strong></h1>"

quick_page_links = """
<H2 style="color: #00ffff;"><u>Live Sensor Readings</u></H2>

<p><span style='background-color: #ccffcc;'>
<a href="/TestSensor" target="_blank">Sensor Readings</a>
</span></p>


<H2 style="color: #00ffff;"><u>Logs</u></H2>

<p><span style='background-color: #ccffcc;'>
<a href="/GetPrimaryLogHTML" target="_blank">Primary Log</a>
</span></p>

<p><span style='background-color: #ccffcc;'>
<a href="/GetNetworkLogHTML" target="_blank">Network Log</a>
</span></p>

<p><span style='background-color: #ccffcc;'>
<a href="/GetSensorsLogHTML" target="_blank">Sensors Log</a>
</span></p>


<H2 style="color: #00ffff;"><u>Downloads</u></H2>

<p><span style='background-color: #ccffcc;'>
<a href="/GetVarianceConfiguration" target="_blank">Download Trigger Variance Configuration</a>
</span></p>

<p><span style='background-color: #ccffcc;'>
<a href="/DownloadSQLDatabase" target="_blank">Download Sensor SQL Database</a>
</span></p>

<H2 style="color: #00ffff;"><u>Initiate Sensor Upgrade</u></H2>

<p><span style='background-color: #ccffcc;'>
<a href="/UpgradeSMB" target="_blank">Upgrade Sensor over SMB</a>
</span></p>

<p><span style='background-color: #ccffcc;'>
<a href="/UpgradeOnline-not" target="_blank">Upgrade Sensor over HTTP</a>
</span></p>
"""

quick_page_final_end = "</body></html>"

# page_sensor_readings.py HTML page components
sensor_readings_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kootnet Sensors || Local Sensors Report</title>
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
"""
