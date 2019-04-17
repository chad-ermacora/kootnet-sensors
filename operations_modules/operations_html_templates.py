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

sensor_test_final_end = """
<span style="color: red"><br/>
** Use 'KootNet Sensors - Control Center' for added descriptions **
</span></p></body></html>
"""

quick_links_html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quick Links</title>
</head>
<body>
<H1><u><span style="color: blueviolet">Local Kootnet Sensor Information & Links</span></u></H1>
"""

# Maybe add later to quick links head with proper colouring elsewhere.
"""
    <style>
        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
"""
"""
<H2><u>Initiate Sensor Upgrade</u></H2>
<p><span><a href="/UpgradeSMB" target="_blank">Upgrade Sensor over SMB</a></span></p>
<p><span><a href="/UpgradeOnline" target="_blank">Upgrade Sensor over HTTP</a></span></p>
"""

quick_links_html_middle = """
<H2><u>Reports & Logs</u></H2>
<p><span><a href="/TestSensor" target="_blank">Sensor Report</a></span></p>
<p><span><a href="/GetPrimaryLogHTML" target="_blank">Primary Log</a></span></p>
<p><span><a href="/GetNetworkLogHTML" target="_blank">Network Log</a></span></p>
<p><span><a href="/GetSensorsLogHTML" target="_blank">Sensors Log</a></span></p>

<H2><u>Downloads</u></H2>
<p><span><a href="/GetVarianceConfiguration" target="_blank">Download Trigger Variance Configuration</a></span></p>
<p><span><a href="/DownloadSQLDatabase" target="_blank">Download Sensor SQL Database</a></span></p>
"""

quick_links_html_end = """
</body>
</html>
"""

quick_links_span_description_start = "<span style='background-color: #00ffff;'>"
quick_links_span_data_start = "<span style='background-color: #ccffcc;'>"
quick_links_span_end = "</span>"
