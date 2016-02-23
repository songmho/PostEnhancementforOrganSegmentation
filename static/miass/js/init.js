/**
 * Created by hanter on 2016. 1. 26..
 */

$(document).ready(function() {
    $('.nav-tabs-group > .nav.navtabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('[data-toggle="tooltip"]').tooltip();
});
