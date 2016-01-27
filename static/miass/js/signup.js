/**
 * Created by hanter on 2016. 1. 27..
 */

var usertype = null;

$(document).ready(function() {
    $('#col-signup-basic').hide();
    $('#col-signup-detail-patient').hide();
    $('#col-signup-detail-physician').hide();


    $('#btn-patient').click(function() {
        usertype = 'patient';
        $('#selectField').removeAttr('required');
        $('#fileQualificiation').removeAttr('required');
        $('#selectGender').attr('required', '');
        $('#inputAge').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });
    $('#btn-physician').click(function() {
        usertype = 'physician';
        $('#selectGender').removeAttr('required');
        $('#inputAge').removeAttr('required');
        $('#selectField').attr('required', '');
        $('#fileQualificiation').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-basic-prev').click(function() {
        usertype = null;

        $('#col-signup-basic').hide();
        $('#col-signup-usertype').show();
    });
    $('#btn-basic-next').click(function() {
        $('#col-signup-basic').hide();
        if (usertype == 'patient') {
            $('#col-signup-detail-patient').show();
        } else if (usertype == 'physician') {
            $('#col-signup-detail-physician').show();
        }
    });

    $('#btn-patient-prev').click(function() {
        $('#col-signup-detail-patient').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-physician-prev').click(function() {
        $('#col-signup-detail-physician').hide();
        $('#col-signup-basic').show();
    })
});