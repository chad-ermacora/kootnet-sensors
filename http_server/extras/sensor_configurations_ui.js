jQuery('#enable_interval_recording').change(function () {
    document.getElementsByName("interval_delay_seconds")[0].disabled = !jQuery(this).prop('checked');
});

jQuery('#enable_custom_temp_offset').change(function () {
    document.getElementsByName("custom_temperature_offset")[0].disabled = !jQuery(this).prop('checked');
});

jQuery('#IP_DHCP').change(function () {
    if (jQuery(this).prop('checked')) {
        document.getElementsByName("ip_address")[0].disabled = true;
        document.getElementsByName("ip_gateway")[0].disabled = true;
        document.getElementsByName("ip_dns1")[0].disabled = true;
        document.getElementsByName("ip_dns2")[0].disabled = true;
    } else {
        document.getElementsByName("ip_address")[0].disabled = false;
        document.getElementsByName("ip_gateway")[0].disabled = false;
        document.getElementsByName("ip_dns1")[0].disabled = false;
        document.getElementsByName("ip_dns2")[0].disabled = false;
    }
});
