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
    $('#btnConfirmReset').click(function () {
        if (!checkPasswordFlag || !checkPasswordConfirmFlag) {
            openModal("Please check your password");
        }
        else {
            $.LoadingOverlay('show');
            $.ajax("/api/user", {
                method: 'POST',
                data: JSON.stringify({
                    action: 'resetPassword',
                    user_id: $('#inputId').val(),
                    password: $('#inputPw').val()
                }),
                dataType: 'json',
                success: function (res) {
                    $.LoadingOverlay('hide');
                    if (res['code'] == 'SUCCESS') {
                        location.replace(mainURL);
                    } else {
                        openFindFailedModal(res['msg']);
                    }
                }
            });
        }

    });

    $('#find-change').click(function () {
        if (bFindId) {
            $('#find-header').text('Find Password');
            $('#find-change').text('Click here to find ID');
            $('#inputId-group').show();
            $('#inputId').attr('required', '');
            bFindId = false;
        } else {
            $('#find-header').text('Find ID');
            $('#find-change').text('Click here to find password');
            $('#inputId-group').hide();
            $('#inputId').removeAttr('required');
            bFindId = true;
        }
    });

    $('#find-form').on('submit', function (e) {
        e.preventDefault();
        $.LoadingOverlay('show');

        var name = $('#inputName').val();
        var email = $('#inputEmail').val();

        if (bFindId) {
            $.ajax("/api/user", {
                method: 'POST',
                data: JSON.stringify({
                    action: 'findid',
                    email: email,
                    name: name
                }),
                dataType: 'json',
                success: function (res) {
                    $.LoadingOverlay('hide');

                    if (res['code'] == 'SUCCESS') {
                        openFindModal('You ID is "' + res['user_id'] + '"', 'Find ID')
                    } else {
                        openFindFailedModal(res['msg']);
                    }
                }
            });
        } else {
            var user_id = $('#inputId').val();

            $.ajax("/api/user", {
                method: 'POST',
                data: JSON.stringify({
                    action: 'findpw',
                    email: email,
                    name: name,
                    user_id: user_id
                }),
                dataType: 'json',
                success: function (res) {
                    $.LoadingOverlay('hide');

                    if (res['code'] == 'SUCCESS') {
                        openResetPasswordModal('You password is "' + res['password'] + '"', 'Find PW')
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
    $('#findModal .modal-body').text(msg);
    $('#findModal').modal();
}

