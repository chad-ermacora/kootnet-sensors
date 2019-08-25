jQuery('#wu_enabled').change(function () {
    if (jQuery(this).prop('checked')) {
        document.getElementsByName("weather_underground_interval")[0].disabled = false;
        document.getElementsByName("weather_underground_outdoor")[0].disabled = false;
        document.getElementsByName("station_id")[0].disabled = false;
        document.getElementsByName("station_key")[0].disabled = false;
    } else {
        document.getElementsByName("weather_underground_interval")[0].disabled = true;
        document.getElementsByName("weather_underground_outdoor")[0].disabled = true;
        document.getElementsByName("station_id")[0].disabled = true;
        document.getElementsByName("station_key")[0].disabled = true;
    }
});
