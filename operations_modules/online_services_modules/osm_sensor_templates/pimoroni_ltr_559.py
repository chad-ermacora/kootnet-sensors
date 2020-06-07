def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni LTR 559 for Open Sense Map registration. """
    return [
        {
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniLTR559",
            "icon": "osem-brightness"
        }
    ]
