var isAccountPage = (user != undefined && user != null && user != {} && user != '');

var checkIDFlag = false;
var checkIDUsed = false;
var tempID = "";
function checkID() {
    var idRe = /^[a-z]+[a-z0-9_.\-]{3,19}$/g;
    var inputId = $('#inputId');
    if (tempID == inputId.val() && checkIDFlag) {
        return
    }
    else {
        tempID = inputId.val()
    }
    if (inputId.val().length < 4) {
        checkIDFlag = false;
        inputId.css("border-color", "red");
        openModal("The length of ID is 4 to 20.", "Checking ID");
        return
    }
    else if (!inputId.val().match(idRe)) {
        checkIDFlag = false;
        inputId.css("border-color", "red");
        openModal("ID must be started with small letters.<br/> And only small letters, digits, and special letters ('-','_','.') are allowed.", "Checking ID");
        return
    }
    else {
        checkIDFlag = true;
        inputId.css("border-color", "");
    }

    checkIDUsed = false;
    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'GET',
        data: {
            action: 'checkId',
            user_id: inputId.val()
        },
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            //console.log(res);
            if (res['code'] == 'SUCCESS') {
                if (!res['existedId'] == false) {
                    inputId.css("border-color", "red");
                    openModal("ID is already existed.", "Checking ID");
                    checkIDUsed = false;
                    checkIDFlag = false;
                } else {
                    openModal("You can use this ID.", "Checking ID");
                    checkIDUsed = true;
                }
            } else {
                inputId.css("border-color", "red");
                openModal("Checking ID is failed. <br/>Please try again.", "Checking ID");
                checkIDUsed = false;
                checkIDFlag = false;
            }
        }
    });
}

var checkPasswordFlag = false;
var checkPasswordConfirmFlag = false;
var tempPassword = "";
function checkPassword() {
    var inputPw = $('#inputPw');

    if(isAccountPage && inputPw.val() == "") { //in account page, no password changed
        checkPasswordFlag = true;
        inputPw.css("border-color", "");
        tempPassword = "";
        if($('#inputPwConfirm').val() == "") {
            checkPasswordConfirmFlag = true;
            $('#inputPwConfirm').css("border-color", "red");
        }
    } else {
        if (tempPassword == inputPw.val() && checkPasswordFlag) {
            return;
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
                content: "The length of Password is greater than 4.",
                placement: "bottom",
                trigger: "manual"
            });
            inputPw.popover("show");
            setTimeout(function () {
                inputPw.popover('destroy');
            }, 3000);
        }
        else {
            checkPasswordFlag = true;
            inputPw.css("border-color", "");
        }
    }

    if(isAccountPage) {
        checkPasswordConfirmFlag = false;
        if($('#inputPwConfirm').val() != '') {
            $('#inputPwConfirm').css("border-color", "red");
            checkPasswordConfirm();
        }
    } else {
        if($('#inputPwConfirm').val() != '') {
            checkPasswordConfirm();
        }
    }
}

function checkPasswordConfirm() {
    console.log('psconfirm');
    var inputPwConfrim = $('#inputPwConfirm');
    if ($('#inputPw').val() != inputPwConfrim.val()) {
        checkPasswordConfirmFlag = false;
        inputPwConfrim.css("border-color", "red");
        inputPwConfrim.popover({
            title: "Warning",
            content: "Confirm Password does not match Password.",
            placement: "bottom",
            trigger: "manual"
        });
        inputPwConfrim.popover("show");
        setTimeout(function () {
            inputPwConfrim.popover('destroy');
        }, 3000);
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

var checkFirstNameFlag = false;
var tempFirstName = "";
function checkFirstName() {
    var inputName = $('#inputFirstName');
    var nameRe = /^[a-zA-Z가-힣 ]{1,200}$/g;
    if (tempFirstName == inputName.val() && checkFirstNameFlag) {
        console.log('same!');
        return;
    }
    else {
        tempFirstName = inputName.val();
        checkFirstNameFlag = false;
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
        }, 3000);
    }
    else {
        checkFirstNameFlag = true;
        inputName.css("border-color", "");
    }
}

var checkLastNameFlag = false;
var tempLastName = "";
function checkLastName() {
    var inputName = $('#inputLastName');
    var nameRe = /^[a-zA-Z가-힣 ]{1,200}$/g;
    if (tempLastName == inputName.val() && checkLastNameFlag) {
        return
    }
    else {
        tempLastName = inputName.val();
        checkLastNameFlag = false;
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
        }, 3000);
    }
    else {
        checkLastNameFlag = true;
        inputName.css("border-color", "");
    }
}

var checkPhoneFlag = false;
var tempPhone = "";
function checkPhone() {
    var inputMobile = $('#inputMobile');
    //var phoneRe = /^[0-9]{4,17}$/;
    var phoneRe = /^\+[0-9]{1,3}\-[0-9]{4,14}?$/g;

    if (tempPhone == inputMobile.val() && checkPhoneFlag)
        return;

    else {
        tempPhone = inputMobile.val();
        checkPhoneFlag = false;
    }
    /*if (inputMobile.val().length < 4) {
        inputMobile.css("border-color", "red");
        inputMobile.popover({
            title: "Warning",
            content: "The length of phone number is greater than 4.",
            placement: "bottom",
            trigger: "manual"
        });
        inputMobile.popover("show");
        setTimeout(function () {
            inputMobile.popover('destroy');
        }, 3000);
    }
    else */if (!inputMobile.val().match(phoneRe)) {
        inputMobile.css("border-color", "red");
        inputMobile.popover({
            title: "Warning",
            content: "The style of phone number is EPP-style. It use the format <br/>+CCC-NNNNNNNN, where C is the 1-3 digit country code, N is up to 14 digits.<br/><br/>For Example )<br/>+1-4108889999<br/>+82-1088889999",
            placement: "bottom",
            trigger: "manual",
            html: true
        });
        inputMobile.popover("show");
        setTimeout(function () {
            inputMobile.popover('destroy');
        }, 10000);
    }
    else {
        checkPhoneFlag = true;
        inputMobile.css("border-color", "");
    }
}

var checkEmailFlag = false;
var checkEmailUsed = -2;
var tempEmail = "";
function checkEmail() {
    var inputEmail = $('#inputEmail');
    var emailRe = /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
    if (tempEmail == inputEmail.val() && checkEmailFlag)
        return;

    else {
        tempEmail = inputEmail.val();
        checkEmailFlag = false;
    }
    if (!inputEmail.val().match(emailRe)) {
        inputEmail.css("border-color", "red");
        openModal("The form of e-mail address is xxxx@xxxx.xxx", 'Email Check');
        return;
    }
    else {
        checkEmailFlag = true;
        inputEmail.css("border-color", "");
    }

    checkEmailUsed = -2;
    var needEmailCheck = true;
    if (isAccountPage) {   //for account change
        if (inputEmail.val() == user['email']) needEmailCheck = false;
        checkEmailUsed = 1;
    }

    if(needEmailCheck) {
        $.LoadingOverlay('show');
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
                $.LoadingOverlay('hide');
                if (res['code'] == 'SUCCESS') {
                    checkEmailUsed = res['emailUsed'];
                } else {
                    checkEmailUsed = -2;
                }

                if (checkEmailUsed == 1) {
                    openModal("You can use this email address.", "Email Check");
                    //pass
                } else if (checkEmailUsed == 0) {
                    var popoverMsg = 'This email is already used for ';
                    if (usertype == 'patient')
                        popoverMsg += 'physician';
                    else
                        popoverMsg += 'patient';
                    //popoverMsg += '. If you are the same person, you just continue. Or not, you should check the email and use another email.';
                    popoverMsg += '.<br/> If you are the same person, you just continue. Or not, you should check the email and use another email.';

                    inputEmail.css("border-color", "orange");
                    openModal(popoverMsg, 'Email Check');

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
                    openModal(popoverMsg, 'EmailCheck');
                }
            }
        });
    }
}

var checkBirthFlag = false;
var tempBirth = "";
function checkBirth() {
    var inputBirthdayMonth = $('#inputBirthdayMonth');
    var inputBirthdayDay = $('#inputBirthdayDay');
    var inputBirthdayYear = $('#inputBirthdayYear');

    if (tempBirth == "" && (!/\S/.test($('#inputBirthdayMonth').val()) ||
                            !/\S/.test($('#inputBirthdayDay').val()) ||
                            !/\S/.test($('#inputBirthdayYear').val()) )) {
        return;
    }

    var month = parseInt($('#inputBirthdayMonth').val());
    var day = parseInt($('#inputBirthdayDay').val());
    var year = parseInt($('#inputBirthdayYear').val());

    if (month == NaN || month <= 0 || month >= 13) {
        inputBirthdayMonth.css("border-color", "red");
        inputBirthdayDay.css("border-color", "red");
        inputBirthdayYear.css("border-color", "red");
        inputBirthdayMonth.popover({
            title: "Warning",
            content: "The month must be 01 to 12.",
            placement: "bottom",
            trigger: "manual"
        });
        inputBirthdayMonth.popover("show");
        setTimeout(function () {
            inputBirthdayMonth.popover('destroy');
        }, 3000);
    }

    if (day == NaN || day <= 0 || day >= 32) {
        inputBirthdayMonth.css("border-color", "red");
        inputBirthdayDay.css("border-color", "red");
        inputBirthdayYear.css("border-color", "red");
        inputBirthdayDay.popover({
            title: "Warning",
            content: "The month must be 01 to 31.",
            placement: "bottom",
            trigger: "manual"
        });
        inputBirthdayDay.popover("show");
        setTimeout(function () {
            inputBirthdayDay.popover('destroy');
        }, 3000);
    }

    if (year == NaN || year <= 1799 || year > new Date().getYear()+1900) {
        inputBirthdayMonth.css("border-color", "red");
        inputBirthdayDay.css("border-color", "red");
        inputBirthdayYear.css("border-color", "red");
        inputBirthdayYear.popover({
            title: "Warning",
            content: "Your birthday may be after 1799 year or before now.",
            placement: "bottom",
            trigger: "manual"
        });
        inputBirthdayYear.popover("show");
        setTimeout(function () {
            inputBirthdayYear.popover('destroy');
        }, 3000);
    }

    var bmonth = month < 10 ? '0'+month : month;
    var bday = day < 10 ? '0'+day : day;
    var birthday = year + '-' + bmonth + '-' + bday;

    if (tempBirth == birthday && checkBirthFlag)
        return;
    else {
        tempBirth = birthday;
        checkBirthFlag = false;
    }

    //var currentTime = new Date().getTime() + 3600 * 9;
    var currentTime = new Date().getTime();
    var minBirthday = -5367427300000;
    var birthdayTime = Date.parse(birthday);

    if (birthdayTime > currentTime || birthdayTime < minBirthday) {
        checkBirthFlag = false;
        inputBirthdayMonth.css("border-color", "red");
        inputBirthdayDay.css("border-color", "red");
        inputBirthdayYear.css("border-color", "red");
        inputBirthdayYear.popover({
            title: "Warning",
            content: "Your birthday may be after 1799 year or before now.",
            placement: "bottom",
            trigger: "manual"
        });
        inputBirthdayYear.popover("show");
        setTimeout(function () {
            inputBirthdayYear.popover('destroy');
        }, 3000);
    }
    else {
        checkBirthFlag = true;
        inputBirthdayMonth.css("border-color", "");
        inputBirthdayDay.css("border-color", "");
        inputBirthdayYear.css("border-color", "");
    }
}

var checkLicenseFlag = false;
var tempLicense = "";
function checkLicense() {
    var inputLicense = $('#inputLicence');
    var licenseRe = /^[\-0-9A-Z]{1,200}$/g;
    if (tempLicense == inputLicense.val() && checkLicenseFlag)
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
        }, 3000);
    }
    else {
        checkLicenseFlag = true;
        inputLicense.css("border-color", "");
    }
}

var checkAddressFlag = true;
function checkAddress() {
    //checkAddressFlag = /\S/.test($('#inputAddress').val());
}

var checkCityFlag = true;
function checkCity() {
    //checkCityFlag = /\S/.test($('#inputCity').val());
}