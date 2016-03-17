/**
 * Created by hanter on 2016. 1. 26..
 */

var SERVER_ADDRESS = 'http://localhost:8000';

$(document).ready(function() {
    $('.nav-tabs-group > .nav.navtabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('.onloading').click(function() {
        $.LoadingOverlay('show');
    });

    $('[data-toggle="tooltip"]').tooltip();
});

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