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
        $('#inputLicence').removeAttr('required');
        $('#fileCertification').removeAttr('required');
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
        $('#inputLicence').attr('required', '');
        $('#fileCertification').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-basic-prev').click(function() {
        usertype = null;

        $('#col-signup-basic').hide();
        $('#col-signup-usertype').show();
    });
    //$('#btn-basic-next').click(function() {
    $('#col-signup-basic').on('submit', function(e) {
        e.preventDefault();
        var idRe = /^[a-z]+[a-z0-9]{3,19}$/g;
        var inputId = $('#inputId');
        if(inputId.val().length > 20 || !inputId.val().match(idRe)) {
            openSignupFailModal("User ID is invalid, please enter small letters and numbers.");
            inputId.focus();
            return;
        }
        var inputPw = $('#inputPw');
        if(inputPw.val().length > 20) {
            openSignupFailModal("Too long password is entered, maximum length is 20.");
            inputPw.focus();
            return;
        }
        var phoneRe = /^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$/g;
        var inputMobile = $('#inputMobile');
        if(!inputMobile.val().match(phoneRe)){
            openSignupFailModal("Please enter valid phone number.");
            inputMobile.focus();
            return;
        }

        //id check
        $.LoadingOverlay('show');
        $.ajax("api/user", {
            method: 'GET',
            data: {
                action: 'checkId',
                user_id: inputId.val()
            },
            dataType: 'json',
            success: function (res) {
                //console.log(res);

                $.LoadingOverlay('hide');
                if (res['code'] == 'SUCCESS') {
                    if (res['existedId']==false) {
                        //pw check
                        if($('#inputPw').val() != $('#inputPwConfirm').val()) {
                            openSignupFailModal("Password Confirm is not same.");
                            return;
                        }

                        $('#col-signup-basic').hide();
                        if (usertype == 'patient') {
                            $('#col-signup-detail-patient').show();
                        } else if (usertype == 'physician') {
                            $('#col-signup-detail-physician').show();
                        }
                    } else {
                        openSignupFailModal("ID is already existed. Please use another ID.")
                    }
                } else {
                    openSignupFailModal("Checking ID is failed. Please try again.")
                }
            }
        });
    });

    $('#btn-patient-prev').click(function() {
        $('#col-signup-detail-patient').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-physician-prev').click(function() {
        $('#col-signup-detail-physician').hide();
        $('#col-signup-basic').show();
    });

    $('#col-signup-detail-patient').on('submit', function(e) {
        e.preventDefault();
        signup('patient');
    });
    $('#col-signup-detail-physician').on('submit', function(e) {
        e.preventDefault();
        signup('physician');
    });
});

function signup(usertype) {
    var user = {};
    user['join_date'] = new Date().getTime();
    user['user_id'] = $('#inputId').val();
    user['password'] = $('#inputPw').val();
    user['name'] = $('#inputName').val();
    user['phone_number'] = $('#inputMobile').val();
    user['email'] = $('#inputEmail').val();
    user['user_type'] = usertype;

    if(usertype == 'patient') {
        user['gender'] = $('#selectGender').val();
        var currentTime = new Date().getTime() + 3600*9;
        var minBirthday = -5367427200000;
        var inputBirthday = $('#inputBirthday');
        console.log(minBirthday)
        if(Date.parse(inputBirthday.val()) > currentTime || Date.parse(inputBirthday.val()) < minBirthday) {
            openSignupFailModal("Your birthday may be after 1800 year or before now.");
            inputBirthday.focus();
            return;
        }
        user['birthday'] = Date.parse(inputBirthday.val());
    } else if(usertype == 'physician') {
        user['medicine_field'] = $('#selectField').val();
        user['license_number'] = $('#inputLicence').val();
        //user['certificate_dir'] = $('#fileCertification').val();
        user['certificate_dir'] = 'here';
    }

    console.log(user);

    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'POST',
        data: JSON.stringify({
            action: 'signup',
            user: user
        }),
        dataType: 'json',
        success: function(res) {
            $.LoadingOverlay('hide');
            if(res['code'] == 'SUCCESS') {
                location.href = indexPage;
            } else {
                openSignupFailModal(res['msg']);
            }
        }
    });
}

function openSignupFailModal(msg, title) {
    if (title!=undefined && title!=null && title!='') {
        $('#signupFailedTitle').text(title)
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Sign up failed. Please try again.'
    }
    $('#signupFailedModal .modal-body').text(msg);
    $('#signupFailedModal').modal();
}