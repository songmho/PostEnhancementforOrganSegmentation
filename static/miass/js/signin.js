/**
 * Created by hanter on 2016. 2. 22..
 */

$(document).ready(function() {
    if($.cookie('remember_user') == 'true') {
        $('#checkRemember').attr('checked', true);
        $('#inputId').val($.cookie('saved_id'));
        $('#inputPw').val($.cookie('saved_pw'));
    }

    $('#btn-auth-resend').click(function() {
        $.LoadingOverlay('show');
        $.ajax("/api/user", {
            method: 'GET',
            data: {
                action: 'resendAuth',
                user_id: $('#inputId').val()
            },
            dataType: 'json',
            success: function(res) {
                $('#signinNeedAuthModal').modal('hide');
                $.LoadingOverlay('hide');
                if(res['code'] == "SUCCESS") {
                    openModal("The email will be sent soon. Please wait a minute.", "Resend Authentication Email");
                } else {
                    openModal(res['msg'], "Resending Error");
                }
            }
        });
    });

    $('#loginForm').on('submit', function(e) {
        e.preventDefault();

        signin();
    });
});

function signin() {
    $.LoadingOverlay('show');
    $.ajax("/api/sessions", {
        method: 'POST',
        data: JSON.stringify({
            user_id: $('#inputId').val(),
            password: $('#inputPw').val()
        }),
        dataType: 'json',
        success: function(res) {
            $.LoadingOverlay('hide');
            if(res['code'] == "SUCCESS") {
                if($('#checkRemember').prop('checked')) {
                    $.cookie('saved_id', $('#inputId').val());
                    $.cookie('saved_pw', $('#inputPw').val());
                    $.cookie('remember_user', true);
                } else {
                    $.cookie('saved_id', '');
                    $.cookie('saved_pw', '');
                    $.cookie('remember_user', false);
                }
                location.href = indexPage;
            } else if (res['code'] == 'NEED_AUTH') {
                $('#signinNeedAuthModal').modal({backdrop: 'static', keyboard: false});
            } else {
                openSignupFailModal(res['msg']);
            }
        }
    });
}


function openSignupFailModal(msg, title) {
    if (title!=undefined && title!=null && title!='') {
        $('#signinFailedTitle').text(title)
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Sign in failed. Please try again.'
    }
    $('#signinFailedModal .modal-body').text(msg);
    $('#signinFailedModal').modal();
}


function openModal(msg, title, action) {
    if (title==undefined || title==null || title=='') {
        $('#alertModalTitle').text('Alert');
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Alert.';
    }
    $('#alertModalTitle').text(title);
    //$('#alertModal .modal-body').text(msg);
    $('#alertModal .modal-body').empty();
    $('#alertModal .modal-body').html(msg);

    if (action != undefined && action != null && jQuery.isFunction(action)) {
        $('#alertModal .modal-alert-close').off('click');
        $('#alertModal .modal-alert-close').unbind('click');
        $('#alertModal .modal-alert-close').click(action);
        $('#alertModal').modal({backdrop: 'static', keyboard: false});
    } else {
        $('#alertModal .modal-alert-close').off('click');
        $('#alertModal .modal-alert-close').unbind('click');
        $('#alertModal').modal();
    }
}