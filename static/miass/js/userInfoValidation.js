var isAccountPage = (user != undefined && user != null && user != {} && user != '');

var checkIDFlag = false;
var checkIDUsed = false;
var checkingIDUsed = false;
var tempID = "";
function checkID() {
    var idRe = /^[a-z]+[a-z0-9_.\-]{3,19}$/g;
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
            content: "ID must be started with small letters, and only small letters, digits, and special letters ('-','_','.') are allowed.",
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

    checkIDUsed = false;
    checkingIDUsed = true;
    $.ajax("/api/user", {
        method: 'GET',
        data: {
            action: 'checkId',
            user_id: inputId.val()
        },
        dataType: 'json',
        success: function (res) {
            //console.log(res);
            if (res['code'] == 'SUCCESS') {
                if (!res['existedId'] == false) {
                    checkIDUsed = false;
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
                } else {
                    checkIDUsed = true;
                }
            } else {
                checkIDUsed = false;
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
            checkingIDUsed = false;
        }
    });
}

var checkPasswordFlag = false;
var tempPassword = "";
function checkPassword() {
    var inputPw = $('#inputPw');

    if(isAccountPage && inputPw.val() == "") { //in account page, no password changed
        checkPasswordFlag = true;
        inputPw.css("border-color", "");
        tempPassword = "";
    } else {
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

    if($('#inputPwConfirm').val() != '') {
        checkPasswordConfirm();
    }
}
var checkPasswordConfirmFlag = false;
function checkPasswordConfirm() {
    var inputPwConfrim = $('#inputPwConfirm');
    if ($('#inputPw').val() != inputPwConfrim.val()) {
        checkPasswordConfirmFlag = false;
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
    else if($('#inputPw').val() == inputPwConfrim.val()) {
        if (isAccountPage) {
            checkPasswordConfirmFlag = true;
            inputPwConfrim.css("border-color", "");
        } else {
            if (inputPwConfrim.val() != "") {
                checkPasswordConfirmFlag = true;
                inputPwConfrim.css("border-color", "");
            }
        }
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
var checkEmailUsed = -2;
var checkingEmailUsed = false;
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
            content: "The form of e-mail address is xxx@xxxx.xxx",
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

    if($('#inputEmailConfirm').val() != '') {
        checkEmailConfirm();
    }

    checkEmailUsed = -2;
    checkingEmailUsed = true;
    var needEmailCheck = true;
    if (isAccountPage) {   //for account change
        if (inputEmail.val() == user['email']) needEmailCheck = false;
        checkEmailUsed = 1;
        checkingEmailUsed = false;
    }

    if(needEmailCheck) {
        $.ajax("/api/user", {
            method: 'GET',
            data: {
                action: 'checkEmail',
                user_type: usertype,
                email: inputEmail.val()
            },
            dataType: 'json',
            success: function (res) {
                //console.log(res);
                if (res['code'] == 'SUCCESS') {
                    checkEmailUsed = res['emailUsed'];
                } else {
                    checkEmailUsed = -2;
                }

                if (checkEmailUsed == 1) {
                    //pass
                } else if (checkEmailUsed == 0) {
                    var popoverMsg = 'This email is already used for ';
                    if (usertype == 'patient')
                        popoverMsg += 'physician';
                    else
                        popoverMsg += 'patient';
                    popoverMsg += '. If you are the same person, you just continue. Or not, you should check the email and use another email.';

                    inputEmail.css("border-color", "orange");
                    inputEmail.popover({
                        title: "Notice",
                        content: popoverMsg,
                        placement: "bottom",
                        trigger: "manual"
                    }).data('bs.popover')
                        .tip()
                        .addClass('popover-info');
                    inputEmail.popover("show");
                    setTimeout(function () {
                        inputEmail.popover('destroy');
                    }, 2000);
                } else { // below -1
                    checkEmailFlag = false;

                    var popoverMsg = 'Unknown error.';
                    switch (checkEmailUsed) {
                        case -2:
                            popoverMsg = 'Checking email is failed. Please try again.';
                            break;
                        case -1:
                            popoverMsg = 'This email is already used.';
                            break;
                    }

                    inputEmail.css("border-color", "red");
                    inputEmail.popover({
                        title: "Warning",
                        content: popoverMsg,
                        placement: "bottom",
                        trigger: "manual"
                    });
                    inputEmail.popover("show");
                    setTimeout(function () {
                        inputEmail.popover('destroy');
                    }, 2000);
                }

                checkingEmailUsed = false;
            }
        });
    }
}

var checkEmailConfirmFlag = false;
function checkEmailConfirm() {
    var inputEmailConfirm = $('#inputEmailConfirm');
    if ($('#inputEmail').val() != inputEmailConfirm.val()) {
        checkEmailConfirmFlag = false;
        inputEmailConfirm.css("border-color", "red");
        inputEmailConfirm.popover({
            title: "Warning",
            content: "Emails are Different.",
            placement: "bottom",
            trigger: "manual"
        });
        inputEmailConfirm.popover("show");
        setTimeout(function () {
            inputEmailConfirm.popover('destroy');
        }, 2000);
    }
    else if($('#inputEmail').val() == inputEmailConfirm.val() && inputEmailConfirm.val()!="") {
        checkEmailConfirmFlag = true;
        inputEmailConfirm.css("border-color", "");
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
    var licenseRe = /^[\-0-9A-Z]{1,200}$/g;
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
            content: "Please enter only digits and upper case alphabets.",
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