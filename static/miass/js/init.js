/**
 * Created by hanter on 2016. 1. 26..
 */

var SERVER_ADDRESS = 'http://203.253.23.26:80';

$(document).ready(function() {
    highlightCurrentMenu();

    $('.nav-tabs-group > .nav.navtabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('textarea.form-control').keyup(function(event) {
        if($(this).val().length > 1000) {
            openModal("Max Textarea Length is 1000", "Alert");
            $(this).val($(this).val().substring(0, 1000));
        }
    });

    $('.onloading').click(function() {
        $.LoadingOverlay('show');
    });

    $('[data-toggle="tooltip"]').tooltip();
});

function openModal(msg, title, action) {
    if (title==undefined || title==null || title=='') {
        $('#alertModalTitle').text('Alert');
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Alert.';
    }
    $('#alertModalTitle').text(title);
    $('#alertModal .modal-body').text(msg);

    if (action != undefined && action != null && jQuery.isFunction(action)) {
        $('#alertModalClose').off('click');
        $('#alertModalClose').unbind('click');
        $('#alertModalClose').click(action);
    }

    $('#alertModal').modal();
}

function highlightCurrentMenu() {
    var paths = jQuery(location).attr('pathname').split('/');

    if(paths.length >= 2) {
        var topMenuPath = paths[1];

        switch(topMenuPath) {
            case 'account':
                $('#nav_account').addClass('selected');
                break;
            case 'profile':
                $('#nav_profile').addClass('selected');
                break;
            case 'archive':
                $('#nav_archive').addClass('selected');
                break;
            case 'interpretation':
                if (paths.length >= 3 && paths[2]=='request') {
                    $('#nav_request').addClass('selected');
                } else {
                    $('#nav_interpretation').addClass('selected');
                }
                break;
            case 'physician':
                $('#nav_physician_profile').addClass('selected');
                break;
            case 'interpretations':
                $('#nav_interpretations').addClass('selected');
                break;
        }
    }
}


//Timestamp -> Datetime Format
String.prototype.string = function(len){var s = '', i = 0; while (i++ < len) { s += this; } return s;};
String.prototype.zf = function(len){return "0".string(len - this.length) + this;};
Number.prototype.zf = function(len){return this.toString().zf(len);};
Date.prototype.format = function(f) {
    if (!this.valueOf()) return " ";

    var d = this;

    return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
        switch ($1) {
            case "yyyy": return d.getFullYear();
            case "yy": return (d.getFullYear() % 1000).zf(2);
            case "MM": return (d.getMonth() + 1).zf(2);
            case "dd": return d.getDate().zf(2);
            case "HH": return d.getHours().zf(2);
            case "hh": return ((h = d.getHours() % 12) ? h : 12).zf(2);
            case "mm": return d.getMinutes().zf(2);
            case "ss": return d.getSeconds().zf(2);
            default: return $1;
        }
    });
};