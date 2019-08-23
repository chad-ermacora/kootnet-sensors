jQuery('#SelectAllCheckboxes').change(function () {
    if (jQuery(this).prop('checked')) {
        jQuery("form input:checkbox").prop('checked', true);
    } else {
        jQuery("form input:checkbox").prop('checked', false);
    }
});
