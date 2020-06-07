def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Sensirion SPS30 for Open Sense Map registration. """
    return [
        {
            "title": "PM1",
            "unit": "µg/m³",
            "sensorType": "SensirionSPS30",
            "icon": "osem-cloud"
        }, {
            "title": "PM2.5",
            "unit": "µg/m³",
            "sensorType": "SensirionSPS30",
            "icon": "osem-cloud"
        }, {
            "title": "PM4",
            "unit": "µg/m³",
            "sensorType": "SensirionSPS30",
            "icon": "osem-cloud"
        }, {
            "title": "PM10",
            "unit": "µg/m³",
            "sensorType": "SensirionSPS30",
            "icon": "osem-cloud"
        }
    ]
