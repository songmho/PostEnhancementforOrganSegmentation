/**
 * Created by hanter on 2016. 2. 22..
 */

$(document).ready(function() {
    if($.cookie('remember_user') == 'true') {
        $('#checkRemember').attr('checked', true);
        $('#inputId').val($.cookie('saved_id'));
        $('#inputPw').val($.cookie('saved_pw'));
    }

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