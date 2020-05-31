def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni PMS5003 for Open Sense Map registration. """
    return [
        {
            "title": "PM1",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        }, {
            "title": "PM2.5",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        }, {
            "title": "PM10",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        }
    ]
