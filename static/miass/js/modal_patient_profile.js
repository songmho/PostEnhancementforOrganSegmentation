/**
 * Created by hanter on 2016. 7. 21..
 */

var paProfiles = null;
var paDetailedProfile = null;

function setPatientProfileModal() {
    console.log(paProfiles);
    for (var type in paProfiles) {
        if (type == 'detail') continue;
        var value = paProfiles[type];
        if(value==undefined || value==null || !/\S/.test(value)) continue;
        $('#' + type).text(getProfileStringForm(type, value));
    }

    if(paProfiles['detail']==undefined || paProfiles['detail']==null)
        return;
    paDetailedProfile = {};
    paDetailedProfile['pmh'] = JSON.parse(paProfiles['detail']['pmh']);
    paDetailedProfile['ed'] = JSON.parse(paProfiles['detail']['ed']);
    paDetailedProfile['sd'] = JSON.parse(paProfiles['detail']['sd']);
    paDetailedProfile['med'] = JSON.parse(paProfiles['detail']['med']);
    paDetailedProfile['fmh'] = JSON.parse(paProfiles['detail']['fmh']);
    paDetailedProfile['alg'] = JSON.parse(paProfiles['detail']['alg']);
    paDetailedProfile['notice'] = paProfiles['detail']['notice'];

    setPastMedicalHistoryTable(paDetailedProfile['pmh']);
    setExistingDiseasesTable(paDetailedProfile['ed']);
    setSuspectedDiseasesTable(paDetailedProfile['sd']);
    setMedicationsTable(paDetailedProfile['med']);
    setFamilyMedicalHistoryTable(paDetailedProfile['fmh']);
    setAllergiesTable(paDetailedProfile['alg']);
    $('#notice').text(paDetailedProfile['notice']);
}

function getPatientProfile(callbackFunc) {
    if (paProfiles == null ) {
        $.LoadingOverlay('show');
        $.ajax("/api/patient_profile", {
            method: 'GET',
            data: {
                user_id: patient['user_id']
            },
            dataType: 'json',
            success: function (res) {
                $.LoadingOverlay('hide');
                if (res['code'] == 'SUCCESS') {
                    paProfiles = res['profiles'];
                    setPatientProfileModal();
                    if(callbackFunc != undefined && callbackFunc != null) {
                        callbackFunc();
                    }
                } else {
                    openModal(res['msg'], 'Getting Patient Profile Failed');
                }
            }
        });
    }
}

function getProfileStringForm(type, value) {
    switch(type) {
        case 'drinkingCapacity':
            return value + ' glasses';
        case 'drinkingFrequency':
            return value + ' times per a week';
        case 'sleeping':
            return value + ' hours per a day';
        case 'exercise':
            return value + ' minutes per a day';
        case 'water':
            return value + ' cups er a day';
        default:
            return value;
    }
}

function setPastMedicalHistoryTable(pmh) {
    var table = $('#table-pmh');
    if (pmh!= null && pmh.length > 0) {
        $('#form-pmh .table-profile-empty').hide();
        $('#form-pmh .table-profile-view').show();
        for (var i = 0; i < pmh.length; i++) {
            var pmhRow = pmh[i];
            var htmlString = "<tr>";
            htmlString += "<td>" + pmhRow['type'] + "</td>";
            htmlString += "<td>" + pmhRow['name'] + "</td>";
            htmlString += "<td>" + pmhRow['date'] + "</td>";
            htmlString += "<td>" + pmhRow['comment'] + "</td>";
            htmlString += "</tr>"
        }
        $('#form-pmh .table-profile-view tbody').append(htmlString);
    } else {
        $('#form-pmh .table-profile-view').hide();
    }
}

function setExistingDiseasesTable(ed) {
    var table = $('#table-ed');
    if (ed!= null && ed.length > 0) {
        $('#form-ed .table-profile-empty').hide();
        $('#form-ed .table-profile-view').show();
        for (var i = 0; i < ed.length; i++) {
            var edRow = ed[i];
            var htmlString = "<tr>";
            htmlString += "<td>" + edRow['name'] + "</td>";
            htmlString += "<td>" + edRow['degree'] + "</td>";
            htmlString += "<td>" + edRow['duration'].replace('|', ' ') + "</td>";
            htmlString += "<td>" + edRow['comment'] + "</td>";
            htmlString += "</tr>"
        }
        $('#form-ed .table-profile-view tbody').append(htmlString);
    } else {
        $('#form-ed .table-profile-view').hide();
    }
}

function setSuspectedDiseasesTable(sd) {
    var table = $('#table-sd');
    if (sd!= null && sd.length > 0) {
        $('#form-sd .table-profile-empty').hide();
        $('#form-sd .table-profile-view').show();
        for (var i = 0; i < sd.length; i++) {
            var sdRow = sd[i];
            var symptoms = sdRow['symptoms'];
            var htmlString = "";
            for (var k = 0; k<symptoms.length; k++) {
                htmlString += "<tr>";
                if (k==0)
                    htmlString += "<td rowspan='" + symptoms.length +"'>" + sdRow['name'] + "</td>";
                htmlString += "<td>" + symptoms[k]['symptom'] + "</td>";
                htmlString += "<td>" + symptoms[k]['degree'].replace('|', ' ') + "</td>";
                htmlString += "<td>" + symptoms[k]['duration'].replace('|', ' ') + "</td>";
                htmlString += "<td>" + symptoms[k]['comment'] + "</td>";
                htmlString += "</tr>"
            }
            $('#form-sd .table-profile-view tbody').append(htmlString);
        }

    } else {
        $('#form-sd .table-profile-view').hide();
    }
}

function setMedicationsTable(med) {
    var table = $('#table-med');
    if (med!= null && med.length > 0) {
        $('#form-med .table-profile-empty').hide();
        $('#form-med .table-profile-view').show();
        for (var i = 0; i < med.length; i++) {
            var medRow = med[i];
            var htmlString = "<tr>";
            htmlString += "<td>" + medRow['name'] + "</td>";
            htmlString += "<td>" + medRow['intake'].replace('|', ' ') + "</td>";
            htmlString += "<td>" + medRow['frequency'].replace('|', ' ') + "</td>";
            htmlString += "<td>" + medRow['duration'].replace('|', ' ') + "</td>";
            htmlString += "<td>" + medRow['comment'] + "</td>";
            htmlString += "</tr>"
        }
        $('#form-med .table-profile-view tbody').append(htmlString);
    } else {
        $('#form-med .table-profile-view').hide();
    }
}

function setFamilyMedicalHistoryTable(fmh) {
    var table = $('#table-fmh');
    if (fmh!= null && fmh.length > 0) {
        $('#form-fmh .table-profile-empty').hide();
        $('#form-fmh .table-profile-view').show();
        for (var i = 0; i < fmh.length; i++) {
            var fmhRow = fmh[i];
            var htmlString = "<tr>";
            htmlString += "<td>" + fmhRow['relationship'] + "</td>";
            htmlString += "<td>" + fmhRow['history'] + "</td>";
            htmlString += "</tr>"
        }
        $('#form-fmh .table-profile-view tbody').append(htmlString);
    } else {
        $('#form-fmh .table-profile-view').hide();
    }
}

function setAllergiesTable(alg) {
    var table = $('#table-alg');
    if (alg!= null && alg.length > 0) {
        $('#form-alg .table-profile-empty').hide();
        $('#form-alg .table-profile-view').show();
        for (var i = 0; i < alg.length; i++) {
            var algRow = alg[i];
            var htmlString = "<tr>";
            htmlString += "<td>" + algRow['name'] + "</td>";
            htmlString += "<td>" + algRow['degree'] + "</td>";
            htmlString += "<td>" + algRow['comment'] + "</td>";
            htmlString += "</tr>"
        }
        $('#form-alg .table-profile-view tbody').append(htmlString);
    } else {
        $('#form-alg .table-profile-view').hide();
    }
}