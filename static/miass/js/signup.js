/**
 * Created by hanter on 2016. 1. 27..
 */

var usertype = null;
var checkIDFlag = false;
var tempID = "";
function checkID() {
    var idRe = /^[a-z]+[a-z0-9]{3,19}$/g;
    var inputId = $('#inputId');
    if ((tempID == inputId.val() || inputId.val().length == 0) && checkIDFlag) {
        return
    }
    else {
        tempID = inputId.val()
    }
    if (inputId.val().length < 4) {
        checkIDFlag = false;
        inputId.css("border-color", "red");
        inputId.popover({
            title: "Warning",
            content: "The length of ID is larger than 4.",
            placement: "bottom",
            trigger: "manual"
        });
        inputId.popover("show");
        setTimeout(function () {
            inputId.popover('destroy');
        }, 2000);
        return
    }
    else if (!inputId.val().match(idRe)) {
        checkIDFlag = false;
        inputId.css("border-color", "red");
        inputId.popover({
            title: "Warning",
            content: "ID must be started with small letters, and only small letters and numbers are allowed.",
            placement: "bottom",
            trigger: "manual"
        });
        inputId.popover("show");
        setTimeout(function () {
            inputId.popover('destroy');
        }, 2000);
        return
    }
    else {
        checkIDFlag = true;
        inputId.css("border-color", "");
    }
    $.LoadingOverlay('show');
    $.ajax("api/user", {
        method: 'GET',
        data: {
            action: 'checkId',
            user_id: inputId.val()
        },
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            if (res['code'] == 'SUCCESS') {
                if (!res['existedId'] == false) {
                    checkIDFlag = false;
                    inputId.css("border-color", "red");
                    inputId.popover({
                        title: "Warning",
                        content: "ID is already existed",
                        placement: "bottom",
                        trigger: "manual"
                    });
                    inputId.popover("show");
                    setTimeout(function () {
                        inputId.popover('destroy');
                    }, 2000);
                }
            } else {
                checkIDFlag = false;
                inputId.css("border-color", "red");
                inputId.popover({
                    title: "Warning",
                    content: "Checking ID is failed. Please try again.",
                    placement: "bottom",
                    trigger: "manual"
                });
                inputId.popover("show");
                setTimeout(function () {
                    inputId.popover('destroy');
                }, 2000);
            }
        }
    });
}

var checkPasswordFlag = false;
var tempPassword = "";
function checkPassword() {
    var inputPw = $('#inputPw');
    if ((tempPassword == inputPw.val() || inputPw.val().length == 0) && checkPasswordFlag) {
        return
    }
    else {
        tempPassword = inputPw.val();
        checkPasswordFlag = false;
    }
    if (inputPw.val().length < 4) {
        checkPasswordFlag = false;
        inputPw.css("border-color", "red");
        inputPw.popover({
            title: "Warning",
            content: "The length of Password is larger than 4.",
            placement: "bottom",
            trigger: "manual"
        });
        inputPw.popover("show");
        setTimeout(function () {
            inputPw.popover('destroy');
        }, 2000);
    }
    else {
        checkPasswordFlag = true;
        inputPw.css("border-color", "");
    }
}

function checkPasswordConfirm() {
    var inputPwConfrim = $('#inputPwConfirm');
    if ($('#inputPw').val() != inputPwConfrim.val()) {
        checkPasswordFlag = false;
        inputPwConfrim.css("border-color", "red");
        inputPwConfrim.popover({
            title: "Warning",
            content: "Passwords are Different.",
            placement: "bottom",
            trigger: "manual"
        });
        inputPwConfrim.popover("show");
        setTimeout(function () {
            inputPwConfrim.popover('destroy');
        }, 2000);
    }
    else {
        checkPasswordFlag = true;
        inputPwConfrim.css("border-color", "");
    }
}

var checkNameFlag = false;
var tempName = "";
function checkName() {
    var inputName = $('#inputName');
    var nameRe = /^[a-zA-Z가-힣 ]{1,200}$/g;
    if ((tempName == inputName.val() || inputName.val().length == 0) && checkNameFlag) {
        return
    }
    else {
        tempName = inputName.val();
        checkNameFlag = false;
    }
    if (!inputName.val().match(nameRe)) {
        inputName.css("border-color", "red");
        inputName.popover({
            title: "Warning",
            content: "Please enter valid user name.",
            placement: "bottom",
            trigger: "manual"
        });
        inputName.popover("show");
        setTimeout(function () {
            inputName.popover('destroy');
        }, 2000);
    }
    else {
        checkNameFlag = true;
        inputName.css("border-color", "");
    }
}

var checkPhoneFlag = false;
var tempPhone = "";
function checkPhone() {
    var inputMobile = $('#inputMobile');
    var phoneRe = /^[0-9]{4,17}$/;
    if ((tempPhone == inputMobile.val() || inputMobile.val().length == 0) && checkPhoneFlag)
        return;

    else {
        tempPhone = inputMobile.val();
        checkPhoneFlag = false;
    }
    if (inputMobile.val().length < 4) {
        inputMobile.css("border-color", "red");
        inputMobile.popover({
            title: "Warning",
            content: "The number of digits is larger than 4.",
            placement: "bottom",
            trigger: "manual"
        });
        inputMobile.popover("show");
        setTimeout(function () {
            inputMobile.popover('destroy');
        }, 2000);
    }
    else if (!inputMobile.val().match(phoneRe)) {
        inputMobile.css("border-color", "red");
        inputMobile.popover({
            title: "Warning",
            content: "Only digits are allowed.",
            placement: "bottom",
            trigger: "manual"
        });
        inputMobile.popover("show");
        setTimeout(function () {
            inputMobile.popover('destroy');
        }, 2000);
    }
    else {
        checkPhoneFlag = true;
        inputMobile.css("border-color", "");
    }
}

var checkEmailFlag = false;
var tempEmail = "";
function checkEmail() {
    var inputEmail = $('#inputEmail');
    var emailRe = /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
    if ((tempEmail == inputEmail.val() || inputEmail.val().length == 0) && checkEmailFlag)
        return;

    else {
        tempEmail = inputEmail.val();
        checkEmailFlag = false;
    }
    if (!inputEmail.val().match(emailRe)) {
        inputEmail.css("border-color", "red");
        inputEmail.popover({
            title: "Warning",
            content: "The form of e-mail address is xxx@Xxxx.xxx",
            placement: "bottom",
            trigger: "manual"
        });
        inputEmail.popover("show");
        setTimeout(function () {
            inputEmail.popover('destroy');
        }, 2000);
    }
    else {
        checkEmailFlag = true;
        inputEmail.css("border-color", "");
    }
}

var checkBirthFlag = false;
var tempBirth = "";
function checkBirth() {
    var inputBirthday = $('#inputBirthday');
    if ((tempBirth == inputBirthday.val() || inputBirthday.val().length == 0) && checkBirthFlag)
        return;

    else {
        tempBirth = inputBirthday.val();
        checkBirthFlag = false;
    }
    var currentTime = new Date().getTime() + 3600 * 9;
    var minBirthday = -5367427200000;
    if (Date.parse(inputBirthday.val()) > currentTime || Date.parse(inputBirthday.val()) < minBirthday) {
        checkBirthFlag = false;
        inputBirthday.css("border-color", "red");
        inputBirthday.popover({
            title: "Warning",
            content: "Your birthday may be after 1799 year or before now.",
            placement: "bottom",
            trigger: "manual"
        });
        inputBirthday.popover("show");
        setTimeout(function () {
            inputBirthday.popover('destroy');
        }, 2000);
    }
    else {
        checkBirthFlag = true;
        inputBirthday.css("border-color", "");
    }
}

var checkLicenseFlag = true;
var tempLicense = "";
function checkLicense() {
    var inputLicense = $('#inputLicence');
    var licenseRe = /^[\-0-9]{1,200}$/g;
    if ((tempLicense == inputLicense.val() || inputLicense.val().length == 0) && checkLicenseFlag)
        return;

    else {
        tempLicense = inputLicense.val();
        checkLicenseFlag = false;
    }
    if (!inputLicense.val().match(licenseRe)) {
        inputLicense.css("border-color", "red");
        inputLicense.popover({
            title: "Warning",
            content: "Please enter only digits.",
            placement: "bottom",
            trigger: "manual"
        });
        inputLicense.popover("show");
        setTimeout(function () {
            inputLicense.popover('destroy');
        }, 2000);
    }
    else {
        checkLicenseFlag = true;
        inputLicense.css("border-color", "");
    }
}

$(document).ready(function () {
    $('#col-signup-basic').hide();
    $('#col-signup-detail-patient').hide();
    $('#col-signup-detail-physician').hide();
    $('#inputBirthday').prop('max', function () {
        return new Date().toJSON().split('T')[0];
    });
    $('#btn-patient').click(function () {
        usertype = 'patient';
        $('#selectField').removeAttr('required');
        $('#inputLicence').removeAttr('required');
        $('#fileCertification').removeAttr('required');
        $('#selectGender').attr('required', '');
        $('#inputAge').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });
    $('#btn-physician').click(function () {
        usertype = 'physician';
        $('#selectGender').removeAttr('required');
        $('#inputAge').removeAttr('required');
        $('#selectField').attr('required', '');
        $('#inputLicence').attr('required', '');
        $('#fileCertification').attr('required', '');
        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-basic-prev').click(function () {
        usertype = null;
        $('#col-signup-basic').hide();
        $('#col-signup-usertype').show();
    });

    $('#col-signup-basic').on('submit', function (e) {
        e.preventDefault();
        var invalidElements = "";
        if (!(checkIDFlag && checkPasswordFlag && checkNameFlag && checkPhoneFlag && checkEmailFlag && checkEmailFlag)) {
            if (!checkIDFlag) {
                invalidElements += "ID"
            }
            if (!checkPasswordFlag) {
                if (invalidElements == "")
                    invalidElements += "Password";
                else
                    invalidElements += ", Password"
            }
            if (!checkNameFlag) {
                if (invalidElements == "")
                    invalidElements += "Name";
                else
                    invalidElements += ", Name"
            }
            if (!checkPhoneFlag) {
                if (invalidElements == "")
                    invalidElements += "Phone Number";
                else
                    invalidElements += ", Phone Number"
            }
            if (!checkEmailFlag) {
                if (invalidElements == "")
                    invalidElements += "E-mail";
                else
                    invalidElements += ", E-mail"
            }
            openModal("Please check these elements;" + invalidElements, "Warning");
        }
        else {
            $('#col-signup-basic').hide();
            if (usertype == 'patient') {
                $('#col-signup-detail-patient').show();
            } else if (usertype == 'physician') {
                $('#col-signup-detail-physician').show();
            }
        }
    });

    $('#btn-patient-prev').click(function () {
        $('#col-signup-detail-patient').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-physician-prev').click(function () {
        $('#col-signup-detail-physician').hide();
        $('#col-signup-basic').show();
    });

    $('#col-signup-detail-patient').on('submit', function (e) {
        e.preventDefault();
        signup('patient');
    });
    $('#col-signup-detail-physician').on('submit', function (e) {
        e.preventDefault();
        signup('physician');
    });
});

function signup(usertype) {
    var user = {};
    if (usertype == 'patient') {
        if (!checkBirthFlag) {
            openModal("Please check birthday.", "Warning");
            return
        }
        user['gender'] = $('#selectGender').val();
        user['birthday'] = Date.parse($('#inputBirthday').val());
    } else if (usertype == 'physician') {
        if (!checkLicenseFlag) {
            openModal("Please check license.", "Warning");
            return
        }
        user['medicine_field'] = $('#selectField').val();
        user['license_number'] = $('#inputLicence').val();
        user['certificate_dir'] = 'here';
    }
    user['join_date'] = new Date().getTime();
    user['user_id'] = $('#inputId').val();
    user['password'] = $('#inputPw').val();
    user['name'] = $('#inputName').val();
    user['phone_number'] = $('#inputMobile').val();
    user['email'] = $('#inputEmail').val();
    user['user_type'] = usertype;

    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'POST',
        data: JSON.stringify({
            action: 'signup',
            user: user
        }),
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            if (res['code'] == 'SUCCESS') {
                location.href = indexPage;
            } else {
                openSignupFailModal(res['msg']);
            }
        }
    });
}

function openSignupFailModal(msg, title) {
    if (title != undefined && title != null && title != '') {
        $('#signupFailedTitle').text(title)
    }
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Sign up failed. Please try again.'
    }
    $('#signupFailedModal .modal-body').text(msg);
    $('#signupFailedModal').modal();
}