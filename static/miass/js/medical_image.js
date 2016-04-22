/**
 * Created by hanter on 2016. 3. 8..
 */
var bRequestIntpr = false;
var reqLevel = 2;

var fileChanged = false;
var imageInfoFormChanged = false;

$(document).ready(function() {
    /*** for file selection ***/
    $('#image_file').change(function() {
        console.log('file changed');
        fileChanged = true;
    });

    $('#imageInfoForm .form-control').change(function() {
        console.log('imageInfoForm changed');
        imageInfoFormChanged = true;
    });

    /*** for edit image info ***/
    $('#takenFrom').change(function() {
        resetTakenLayout();
    });
    resetTakenLayout();

    $('#btnImageFile').click(function() {
        var fileForm = $('#image_file');
        fileForm.val('');       //reset file form

        $('#imageUploadModal').modal();
    });

    setOpenImageViewerListener($('#image-previewer'));

    $('#btnFormEdit').click(function() {
        fileChanged = false;
        imageInfoFormChanged = false;

        $('#btnFormEdit').hide();
        $('#btnFormDelete').hide();
        $('#btnFormEditConfirm').show();
        $('#btnFormCancel').show();
        $('#subject').removeAttr('readonly');
        $('#imageType').removeAttr('disabled');
        $('#btnImageFile').removeAttr('disabled');
        $('#image_file').val('');
        $('#takenDate').removeAttr('readonly');
        $('#takenFrom').removeAttr('disabled');
        $('#takenPhysicianName').removeAttr('readonly');
        $('#medicalDepartment').removeAttr('readonly');
        $('#clinicName').removeAttr('readonly');
        $('#imageDescription').removeAttr('readonly');
    });

    $('#imageInfoForm').on('submit', function(e) {
        e.preventDefault();

        $('#btnFormEditConfirm').hide();
        $('#btnFormCancel').hide();
        $('#btnFormEdit').show();
        $('#btnFormDelete').show();
        $('#subject').attr('readonly', '');
        $('#imageType').attr('disabled', '');
        $('#btnImageFile').attr('disabled', '');
        $('#takenDate').attr('readonly', '');
        $('#takenFrom').attr('disabled', '');
        $('#takenPhysicianName').attr('readonly', '');
        $('#clinicName').attr('readonly', '');
        $('#medicalDepartment').attr('readonly', '');
        $('#imageDescription').attr('readonly', '');
        
        if (imageInfoFormChanged) {
            if (fileChanged) {
                //if file is changed, image type must be corresponded
                var imageType = $('#imageType').val();
                var filenames = getFiles($('#image_file'));
                for (var i=0; i<filenames.length; i++) {
                    var ext = getFileExtension(filenames[i]);
                    if (!checkImageTypeAndExtension(imageType, ext)) {
                        console.log(ext);
                        $('#imageUploadModal').modal('hide');
                        openModal('Please upload correct image files for image type.', 'Image Type Check');
                        return;
                    }
                }
            } else {
                //if also file is not changed, image type must be corresponded
                if (checkImageTypeIsGraphic($('#imageType').val())
                        != checkImageTypeIsGraphic(imageInfo.image_type)) {
                    $('#imageUploadModal').modal('hide');
                    openModal('Please select correct image type for uploaded image files.', 'Image Type Check');
                    return;
                }
            }

            var nowImageInfo = {
                user_id: user['user_id'],
                image_id: imageInfo.image_id,
                subject: $('#subject').val(),
                image_type: $('#imageType').val(),
                taken_date: Date.parse($('#takenDate').val()),
                taken_from: $('#takenFrom').val(),
                physician: $('#takenPhysicianName').val(),
                place: $('#clinicName').val(),
                medical_department: $('#medicalDepartment').val(),
                description: $('#imageDescription').val()
            };

            $.LoadingOverlay('show');
            $.ajax("/api/medical_image", {
                method: 'PUT',
                data: JSON.stringify({
                    action: 'update',
                    image_info: nowImageInfo
                }), dataType: 'json'
                , success: function (res) {
                    $.LoadingOverlay('hide');
                    if (res['code'] == 'SUCCESS') {
                        imageInfo.subject = nowImageInfo.subject;
                        imageInfo.image_type = nowImageInfo.image_type;
                        imageInfo.taken_date = nowImageInfo.taken_date;
                        imageInfo.taken_from = nowImageInfo.taken_from;
                        imageInfo.physician = nowImageInfo.physician;
                        imageInfo.place = nowImageInfo.place;
                        imageInfo.description = nowImageInfo.description;
                        resetImageInfo();

                        if (fileChanged && $('#image_file').val()!="") {
                            $('#formUpdateFile').submit();
                        } else {
                            openModal('Updating image information is succeed.', "Update Image");
                        }
                        //resetViewer();
                    } else {
                        openModal(res['msg'], "Updating Image Failed");
                        resetImageInfo();
                    }
                }
            });
        } else if (fileChanged && $('#image_file').val()!="") {
            $('#formUpdateFile').submit();
        }
    });



    $('#formUpdateFile').on('submit', function(e) {
        e.preventDefault();

        var imageType = $('#imageType').val();
        var filenames = getFiles($('#image_file'));
        for (var i=0; i<filenames.length; i++) {
            var ext = getFileExtension(filenames[i]);
            if (!checkImageTypeAndExtension(imageType, ext)) {
                console.log(ext);
                $('#imageUploadModal').modal('hide');
                openModal('Please upload correct image files for image type.', 'Image Type Check');
                return;
            }
        }

        var data = new FormData($('#formUpdateFile').get(0));
        data.append('action', 'update');
        data.append('image_info', JSON.stringify(imageInfo));

        var xprogressID = new Date().getTime();
        //setTimeout(function() {
            startFileProgressUpdate(xprogressID);
        //}, 100);

        $('#imageUploadModal').modal('hide');

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

                console.log(uploadStatus);
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
                    imageInfo['image_dir'] = res['new_dir'];
                    resetViewer();
                    openModal('The new file is successfully uploaded', 'Update Success');
                } else {
                    openModal(res['msg'], 'Update Failed');
                }
            }
        });
    });

    $('#imageUploadModalCancel').click(function() {
        fileChanged = false;
        $('#image_file').val('');
    });

    $('#btnFormCancel').click(function() {
        fileChanged = false;
        imageInfoFormChanged = false;
        $('#btnFormEditConfirm').hide();
        $('#btnFormCancel').hide();
        $('#btnFormEdit').show();
        $('#btnFormDelete').show();
        $('#subject').attr('readonly', '');
        $('#imageType').attr('disabled', '');
        $('#btnImageFile').attr('disabled', '');
        $('#takenDate').attr('readonly', '');
        $('#takenFrom').attr('disabled', '');
        $('#takenPhysicianName').attr('readonly', '');
        $('#clinicName').attr('readonly', '');
        $('#medicalDepartment').attr('readonly', '');
        $('#imageDescription').attr('readonly', '');
        resetImageInfo();
        resetTakenLayout();
    });

    $('#btnDeleteCofirm').click(function() {
        $.LoadingOverlay('show');
        $.ajax("/api/medical_image?user_id="+user['user_id']+"&image_id="+imageInfo['image_id']
                +"&image_dir="+imageInfo['image_dir'], {
            method: 'DELETE',
            success: function (res) {
                if(res['code'] == 'SUCCESS') {
                    location.replace(archiveURL);
                } else {
                    $.LoadingOverlay('hide');
                    openModal(res['msg'], "Delete Failed");
                }
            }
        });
    });

    /*** for interpretation request ***/
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
            $('#medicalDepartmentGroup').hide();
        } else {
            $('#reqSubject').attr('required', '');
            $('#reqMessage').attr('required', '');
            $('#reqSubjectGroup').show();
            $('#reqMessageGroup').show();
            $('#medicalDepartmentGroup').show();
        }
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
                    openModal('Request interpretation success.', "Request Success", location.replace(requestListURL));
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

function resetImageInfo() {
    $('#subject').val(imageInfo.subject);
    $('#imageType').val(imageInfo.image_type);
    $('#takenDate').val(new Date(imageInfo.taken_date).format("yyyy-MM-dd"));
    $('#takenFrom').val(imageInfo.taken_from);
    $('#takenPhysicianName').val(imageInfo.physician);
    $('#clinicName').val(imageInfo.place);
    $('#imageDescription').val(imageInfo.description);
}

function resetTakenLayout() {
    var tf = $('#takenFrom').val();
    if(tf == 'Home') {
        $('#takenPhysicianName').removeAttr('required').val('');
        $('#clinicName').removeAttr('required').val('');
        $('#medicalDepartmentGroup').removeAttr('required').val('');
        $('#physicianGroup').css('visibility', 'hidden');
        $('#clinicNameGroup').css('visibility', 'hidden');
        $('#medicalDepartmentGroup').css('visibility', 'hidden');
    } else {
        $('#takenPhysicianName').attr('required', '');
        $('#clinicName').attr('required', '');
        $('#medicalDepartmentGroup').attr('required', '');
        $('#physicianGroup').css('visibility', 'visible');
        $('#clinicNameGroup').css('visibility', 'visible');
        $('#medicalDepartmentGroup').css('visibility', 'visible');
    }
}

function openDeleteConfirmModal() {
    $('#deleteImageConfirmModal').modal();
}
