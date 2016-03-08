/**
 * Created by hanter on 2016. 3. 8..
 */

var bRequestIntpr = false;
var reqLevel = 2;


$(document).ready(function() {
    $('#btnRequest').click(function() {
        if(bRequestIntpr) {
            bRequestIntpr = false;
            $('#btnRequest').text('Request Interpretation');
            $('#requestIntprForm').slideUp(600);
        } else {
            bRequestIntpr = true;
            $('#btnRequest').text('Cancel Request');
            $('#reqSubject').val('');
            $('#reqMessage').val('');

            $('#requestIntprForm').slideDown(600);
        }
    });

    $('#reqLevel').change(function() {
        reqLevel = $(this).val();
        if(reqLevel == 1) {
            $('#reqSubject').removeAttr('required').val('');
            $('#reqMessage').removeAttr('required').val('');
            $('#reqSubjectGroup').hide();
            $('#reqMessageGroup').hide();
        } else {
            $('#reqSubject').attr('required', '');
            $('#reqMessage').attr('required', '');
            $('#reqSubjectGroup').show();
            $('#reqMessageGroup').show();
        }
    });

    $('#imageInfoForm').on('submit', function(e) {

    });

    $('#requestIntprForm').on('submit', function(e) {
        e.preventDefault();

        var reqData;
        reqLevel = $('#reqLevel').val();
        if (reqLevel == 1) {
            reqData = JSON.stringify({
                action: 'patientReq',
                image_id: imageInfo.image_id,
                subject: '',
                message: '',
                level: reqLevel
            });
        } else {
            reqData = JSON.stringify({
                action: 'patientReq',
                image_id: imageInfo.image_id,
                subject: $('#reqSubject').val(),
                message: $('#reqMessage').val(),
                level: reqLevel
            });
        }

        $.LoadingOverlay('show');
        $.ajax("/api/interpretation", {
            method: 'PUT',
            data: reqData,
            dataType: 'json',
            success: function (res) {
                $.LoadingOverlay('hide');
                if(res['code'] == 'SUCCESS') {
                    openModal('Request interpretation success.', "Request Success");
                } else {
                    openModal(res['msg'], "Request Failed");
                }
            }
        });
    });

    $('#btnFormDelete').click(function() {
        openDeleteConfirmModal();
    });
    $('#btnDeleteCofirm').click(function() {
        //$.LoadingOverlay('show');
    });
});

function openModal(msg, title) {
    if (title==undefined || title==null || title=='') {
        $('#alertModalTitle').text('Alert');
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Alert.';
    }
    $('#alertModalTitle').text(title);
    $('#alertModal .modal-body').text(msg);
    $('#alertModal').modal();
}

function openDeleteConfirmModal() {
    $('#deleteImageConfirmModal').modal();
}