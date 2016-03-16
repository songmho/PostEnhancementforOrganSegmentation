/**
 * Created by hanter on 2016. 3. 8..
 */

$(document).ready(function() {
    circleProgress = new ProgressBar.Circle('#uploadProgress', {
        color: '#D76474',
        strokeWidth: 3,
        trailWidth: 1,
        text: {
            value: '0'
        },
        step: function(state, bar) {
            bar.setText((bar.value() * 100).toFixed(0));
        }
    });

    $('#uploadImageForm').on('submit', function(e) {
        e.preventDefault();
        var currentTime = new Date().getTime();
        var minDate = 0;
        var imageDate = $('#takenDate');
        if(Date.parse(imageDate.val()) > currentTime || Date.parse(imageDate.val()) < minDate) {
            openUploadFailedModal("Invalid Date");
            imageDate.focus();
            return;
        } else{
            console.log("rRR")
        }


        var data = new FormData($('#uploadImageForm').get(0));
        data.append('action', 'upload');
        data.append('image_info', JSON.stringify({
            user_id : user['user_id'],
            subject : $('#subject').val(),
            image_type : $('#imageType').val(),
            taken_date: Date.parse(imageDate.val()),
            taken_from : $('#takenFrom').val(),
            physician : $('#takenPhysicianName').val(),
            place : $('#clinicName').val(),
            description : $('#imageDescription').val()
        }));
        //console.log(data);

        var xprogressID = new Date().getTime();
        setTimeout(function() {
            startFileProgressUpdate(xprogressID);
        }, 100);

        setProgressText('Uploading...');
        $('#uploadingProgressModal').modal({
            backdrop: 'static',
            keyboard: false
        });

        $.ajax({
            url: $(this).attr('action') + '?X-Progress-ID='+xprogressID,
            type: $(this).attr('method'),
            data: data,
            cache: false,
            processData: false,
            contentType: false,
            success: function(res) {
                //console.log(res);
                if (uploadStatus <= 2) {
                    stopFileProgressUpdate(false);
                    setTimeout(function () {
                        $('#uploadingProgressModal').modal('hide');
                    }, 200);
                } else {
                    stopRotatingProgress();
                    $('#uploadingProgressModal').modal('hide');
                }
                uploadStatus=0;

                if (res['code'] == 'SUCCESS') {
                    $.LoadingOverlay('show');
                    location.href = archiveURL;
                } else {
                    openUploadFailedModal(res['msg']);
                }
            }
        });
    });

    $('#takenFrom').change(function() {
        var tf = $(this).val();
        if(tf == 'Home') {
            $('#takenPhysicianName').removeAttr('required').val('');
            $('#clinicName').removeAttr('required').val('');
            $('#physicianGroup').hide();
            $('#clinicNameGroup').hide();
        } else {
            $('#takenPhysicianName').attr('required', '');
            $('#clinicName').attr('required', '');
            $('#physicianGroup').show();
            $('#clinicNameGroup').show();
        }
    });

});

function openUploadFailedModal(msg) {
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Uploading Medical Image Failed.';
    }
    $('#uploadFailModal .modal-body').text(msg);
    $('#uploadFailModal').modal();
}

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
