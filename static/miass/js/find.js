/**
 * Created by hanter on 2016. 3. 1..
 */

var bFindId = true;
$(document).ready(function () {

    $('#inputPw').blur(function () {
        checkPassword();
    });
    $('#inputPwConfirm').blur(function () {
        checkPasswordConfirm();
    });

    $('#find-change').click(function () {
        if (bFindId) {
            $('#find-header').text('Find Password');
            $('#find-change').text('Click here to find ID');
            $('#selectType-group').hide();
            $('#selectType').removeAttr('required');
            $('#inputId-group').show();
            $('#inputId').attr('required', '');
            bFindId = false;
        } else {
            $('#find-header').text('Find ID');
            $('#find-change').text('Click here to find password');
            $('#inputId-group').hide();
            $('#inputId').removeAttr('required');
            $('#selectType-group').show();
            $('#selectType').attr('required', '');
            bFindId = true;
        }
    });

    $('#find-form').on('submit', function (e) {
        e.preventDefault();
        $.LoadingOverlay('show');

        if (bFindId) {
            var type = $('#selectType').val();
            var email = $('#inputEmail').val();

            $.ajax("/api/user", {
                method: 'POST',
                data: JSON.stringify({
                    action: 'findid',
                    user_type: type,
                    email: email
                }),
                dataType: 'json',
                success: function (res) {
                    $.LoadingOverlay('hide');

                    if (res['code'] == 'SUCCESS') {
                        openFindModal('Your ID is "<b style="color: #d76474;">' + res['user_id'] + '</b>".', 'Find ID')
                    } else {
                        openFindFailedModal(res['msg']);
                    }
                }
            });
        } else {
            var user_id = $('#inputId').val();
            var email = $('#inputEmail').val();

            $.ajax("/api/user", {
                method: 'POST',
                data: JSON.stringify({
                    action: 'findpw',
                    email: email,
                    user_id: user_id
                }),
                dataType: 'json',
                success: function (res) {
                    $.LoadingOverlay('hide');

                    if (res['code'] == 'SUCCESS') {
                        openFindModal('Temporary password will be sent to your email. Please wait a minute.', 'Find Password')
                    } else {
                        openFindFailedModal(res['msg']);
                    }
                }
            });
        }
    });

});

function openFindFailedModal(msg) {
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Finding ID or PW is failed.'
    }
    $('#findFailedModal .modal-body').text(msg);
    $('#findFailedModal').modal();

}
function openResetPasswordModal(msg) {
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Finding ID or PW is failed.'
    }
    $('#inputPwConfirm').css("border-color", "");
    $('#inputPw').css("border-color", "");
    checkPasswordFlag = false;
    $('#resetPasswordModal').modal();
}

function openFindModal(msg, title) {
    if (title != undefined && title != null && title != '') {
        $('#findModalTitle').text(title)
    }
    if (msg == undefined || msg == null || msg == '') {
        msg = '...'
    }
    $('#findModal .modal-body').html(msg);
    $('#findModal').modal();
}

